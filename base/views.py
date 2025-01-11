from django.shortcuts import render, redirect, HttpResponse
from .forms import ParticipantForm, PropertyForm
from .models import Participant, Item, Bidding, Result
from .utils import *
from django.core.mail import send_mail, EmailMessage
from DTProj.settings import EMAIL_HOST_USER 
from django.urls import reverse
from django.http import HttpResponseForbidden
from django.contrib import messages
from decimal import Decimal
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.contrib.staticfiles import finders
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors


def home(request):
    return render(request, 'main.html')

def register(request):
    return render (request, 'Register.html')

def submit_form(request):
    
    if request.method == 'POST':
        
        participant_form = ParticipantForm(request.POST)
        property_form = PropertyForm(request.POST)

        if participant_form.is_valid() and property_form.is_valid():
            
            items = generate_unique_id_item()
            
            participants = participant_form.save(items=items)
            for participant in participants:
                participant.save()
                
            properties = property_form.save(items=items)
            for property_instance in properties:
                property_instance.save()

            send_mail_to_participants(
                subject='Sealed Bid',
                sender='mainig87@gmail.com',
                item_id=items,
            )
            
            success = 'Registration has been successfully completed. Please check your email.'
            return render(request, 'successMsg.html', {'success_message': success})

def send_mail_to_participants(subject, sender, item_id, fail_silently=False):
    # Fetch the most recently registered participants with the same itemID from the database
    participants = Participant.objects.filter(IDItems=item_id)

    # Send email to recently registered participants
    for participant in participants:
        # Construct the personalized URL based on the participant's IDParticipants
        bidding_url = reverse('bidding', args=[participant.IDParticipants])

        # Create the email message
        email_message = f"Greetings {participant.first_name}!\n\n" \
                        f"Attached here is the link that you will be using for bidding:\n" \
                        f"http://127.0.0.1:8000{bidding_url}\n\n" \
                        f"Good luck and may you get what you desire!"

        # Send email to the participant
        send_mail(subject, email_message, sender, [participant.email], fail_silently=fail_silently)

def bidding(request, bidding_url):
    participant = Participant.objects.filter(IDParticipants=bidding_url).first()

    if participant:
        return render(request, 'JoinBidding.html', {'participant': participant})
    else:
        return HttpResponseForbidden("You are not authorized to access this page.")

def agreement(request, bidding_url):
    participant = Participant.objects.filter(IDParticipants=bidding_url).first()

    if not participant:
        return HttpResponseForbidden("You are not authorized to access this page.")

    if request.method == 'POST':
        entered_password = request.POST.get('password')
        participant_password = request.POST.get('participant_password')

        if entered_password == participant_password:
            return render(request, 'agtPage.html', {'participant': participant})
        
        else:
            messages.error(request, 'Incorrect password. Please try again.')
            return render(request, 'JoinBidding.html', {'participant': participant})
    
def auction(request, bidding_url):
    participants = Participant.objects.filter(IDParticipants=bidding_url).first()
    properties = Item.objects.filter(Items_ID=participants.IDItems)
    getItems = []

    if not participants:
        return HttpResponseForbidden("You are not authorized to access this page.")

    if request.method == 'POST':
        for property in properties:
            item_id = str(property.id)
            bid_amount_key = 'bid_amount_' + item_id
            bid_amount = request.POST.get(bid_amount_key)

            # Check if input bid is less than min bid amount
            if property.min_bid is not None and Decimal(bid_amount) < property.min_bid:
                messages.error(request, 'Bid is less than the minimum bid amount. Please try again.')
                return render(request, 'biddingPage.html', {'participant': participants, 'properties': properties, 'error_message': f'Bid must be equal to or greater than the minimum bid of ${property.min_bid} for {property.property_name}.'})

            getItems.append(bid_amount)

        # Dynamically calculate total and create Bidding instance
        total = sum(int(bid_amount) for bid_amount in getItems)
        bidding_data = {'IDParticipant': participants.IDParticipants, 'total': total}
        for i, bid_amount in enumerate(getItems, start=1):
            bidding_data[f'item{i}'] = int(bid_amount)

        CurrentAuction = Bidding(**bidding_data)
        CurrentAuction.save()

        participant = Participant.objects.get(IDParticipants=bidding_url)
        myItems = list(Item.objects.filter(Items_ID = participant.IDItems)) # Store the valued items in this list
        getParticipants = list(Participant.objects.filter(IDItems = participant.IDItems)) # To store the participants in the bid
        value_items =[] # Store all the items value of each participants 
        total_items = [] # Store the total value per participants which they declared for each item

        for get_participant in getParticipants:
            participant_check2 = Bidding.objects.filter(IDParticipant=get_participant.IDParticipants) #checking if the participant exist in the bid or not
            value_items1 =[] # 1d array that collect all the declared value per item
                
            #if exist then will now process the getting the information inputted
            if participant_check2.exists():
                currentParticipant = Bidding.objects.get(IDParticipant = get_participant.IDParticipants)             
                total_items.append(currentParticipant.total)
                if currentParticipant.item1 > 0:
                    value_items1.append(currentParticipant.item1)
                if currentParticipant.item2 > 0:
                    value_items1.append(currentParticipant.item2)
                if currentParticipant.item3 > 0:
                    value_items1.append(currentParticipant.item3)
                if currentParticipant.item4 > 0:
                    value_items1.append(currentParticipant.item4)
                if currentParticipant.item5 > 0:
                    value_items1.append(currentParticipant.item5)
                if currentParticipant.item6 > 0:
                    value_items1.append(currentParticipant.item6)
                if currentParticipant.item7 > 0:
                    value_items1.append(currentParticipant.item7)
                if currentParticipant.item8 > 0:
                    value_items1.append(currentParticipant.item8)
                if currentParticipant.item9 > 0:
                    value_items1.append(currentParticipant.item9)
                if currentParticipant.item10 > 0:
                    value_items1.append(currentParticipant.item10)
                value_items.append(value_items1) # an array that will store in an array
            else:
                success = 'You successfully placed  your bid. Please wait for the result in your email.'
                return render(request, 'successMsg.html', {'success_message': success})
                

        total_value = [] # total value awarded
        amount = [] # amount they get or pay
        fair_share =[] # fair share
        final_amount =[] # amount minus the surplus
        participant_wonId =[] # participant id
        participant_wonFirstName = [] # participant first name
        participant_wonLastName = [] # participant last name
        participant_wonEmail=[] # participant last name
        item_won=[] # what items they won
        participant_link = [] # link they will get when send
        pay = []
        get = []
        largest = []

        # loop for storing the information in an array from get_participants
        for getParticipant in getParticipants:
            participant_wonId.append(getParticipant.IDParticipants)
            participant_wonFirstName.append(getParticipant.first_name)
            participant_wonLastName.append(getParticipant.last_name)
            participant_wonEmail.append(getParticipant.email)
            participant_link.append(getParticipant.IDParticipants+getParticipant.IDItems)

        #loop for just getting the length of an array the values will change in the process   
        for x in range(len(getParticipants)):
            total_value.append(0)
            final_amount.append(0)
            amount.append(0)
            pay.append(0)
            get.append(0)
            item_won.append('')
            fairShare = total_items[x] / len(getParticipants)
            rounded = round(fairShare, 2)
            fair_share.append(rounded)
        
        count = 0
        while count < len(myItems):
            values = [sublist[count] for sublist in value_items]  # storing the subarray in a 2D array
            max_value = max(values)  # finding the highest value
            indices = [i for i, v in enumerate(values) if v == max_value]  # find indices with the highest value

            if len(indices) > 1:  # if there is a tiebreaker
                random_winner_index = random.choice(indices)
                myItemm = myItems[count]
                total_value[random_winner_index] += max_value
                item_won[random_winner_index] = myItemm.property_name + ' ' + item_won[random_winner_index]
            else:
                # loop for finding its position and declare it with that item
                for i in range(len(values)):
                    if values[i] == max_value:
                        myItemm = myItems[count]
                        total_value[i] += max_value
                        item_won[i] = myItemm.property_name + ' ' + item_won[i]

            count += 1  

        for y in range(len(getParticipants)):
            amount[y] = total_value[y] - fair_share[y] # total value awarded - fair share

        #finding its surplus by totaling its amount
        surplus = sum(amount)
            
        # will split the surplus depending on the participants
        surplus_split = surplus/len(getParticipants)
            
        #rounding it off by 2 decimal places
        rounded_surplus = round(surplus_split, 2)
            
        # loop for the final amount they will pay - surplus
        for y in range(len(getParticipants)):
            final_amount[y] = amount[y] - rounded_surplus
            if final_amount[y]>0:
                pay[y] = round(final_amount[y], 2)
            else:
                get[y] = round(abs(final_amount[y]), 2)
        
        for y in range(len(getParticipants)):
            participant_data = {
                'fName': participant_wonFirstName[y],
                'lName': participant_wonLastName[y],
                'email': participant_wonEmail[y],
                'IDparticipants': participant_wonId[y],
                'item': item_won[y],
                'total_value': total_value[y],
                'fair_share': fair_share[y],
                'pay': pay[y],
                'get': get[y],
                'link': participant_link[y],
            }

            # Save auction result data to the database
            auction_result = Result(**participant_data)
            auction_result.save()

            # Send an email with the PDF attachment
            send_auction_result_email(participant_data)

        success = 'Auction results successfully processed and emails sent.'
        return render(request, 'successMsg.html', {'success_message': success})

    return render(request, 'biddingPage.html', {'participant': participants, 'properties': properties})

def send_auction_result_email(participant_data):

    pdf_content = generate_pdf(participant_data)

    email = EmailMessage(
        'AUCTION RESULT',
        f'Greetings!\n\n'
        f'This is the properties settlement team. We are excited to inform you that the results of your bidding are now available. '
        f'Please find attached the PDF with detailed information about your auction results. You can download and review the document at your convenience.\n\n'
        f'Thank you for participating in the auction!\n\n'
        f'Best regards,\n'
        f'Your Properties Settlement Team',
        'from@example.com',
        [participant_data['email']],
    )
    
    email.attach('auction_result.pdf', pdf_content.getvalue(), 'application/pdf')
    email.send() 

def generate_pdf(participant_data):
    # Create a file-like buffer to receive PDF data.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="auction_result.pdf"'

    p = canvas.Canvas(response, pagesize=letter)
    current_date = datetime.now().strftime("%m-%d-%Y")

    image_path = finders.find('files/PS-brand.png')
    width, height = 400, 85
    x_offset = (letter[0] - width) / 2
    y_offset = letter[1] - height - 40
    p.drawImage(image_path, x_offset, y_offset, width, height)
    
    y = y_offset - 50
    header_width = p.stringWidth(f"SEALEAD BID AUCTION", "Times-Bold", 20)
    x = (letter[0] - header_width) / 2
    p.setFont("Times-Bold", 20)
    p.drawString(x, y, f"SEALED BID AUCTION")
    
    h_width = p.stringWidth(f"Result for {participant_data['fName']}", "Times-Bold", 20)
    h_widthx = (letter[0] - h_width) / 2
    p.setFont("Times-Bold", 20)
    p.drawString(h_widthx, 595, f"Result for {participant_data['fName']}")
    
    p.setFont("Times-Roman", 14)
    p.drawString(90, 535, f"Full Name: {participant_data['fName']} {participant_data['lName']}")
    p.drawString(430, 535, f"Date: {current_date}")
    p.drawString(90, 515 , f"Email: {participant_data['email']}")
    p.drawString(430, 515 , f"ID: {participant_data['IDparticipants']}")
    
    table_data = [
        ['Total Value:', f"${participant_data['total_value']}"],
        ['Fair Share:', f"${participant_data['fair_share']}"],
        ['Pay:', f"${participant_data['pay']}"],
        ['Get:', f"${participant_data['get']}"],
        ['Item/s Won:', ''],
        [f"{participant_data['item']}", ''],
    ]
    rowHeights = [40, 40, 40, 40, 40, 40] 
    table = Table(table_data, colWidths=[200, 200], rowHeights=rowHeights)

    style = TableStyle([
        ('SPAN', (0, 4), (1, 4)), 
        ('SPAN', (0, 5), (1, 5)),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'), 
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, -1), 'Times-Bold'), 
        ('FONTSIZE', (0, 0), (-1, -1), 16),  
        ('BOX', (0, 0), (-1, -1), 0.50, colors.black),
    ])
    table.setStyle(style)
    
    table_width, table_height = table.wrapOn(p, 0, 0)
    tableX = (letter[0] - table_width) / 2
    table.drawOn(p, tableX, 240)  
    
    p.showPage()
    p.save()

    return response
  