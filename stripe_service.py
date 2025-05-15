import os
import stripe
from flask import url_for

# Set the Stripe API key
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

def get_domain():
    """Get the domain based on environment"""
    replit_deployment = os.environ.get('REPLIT_DEPLOYMENT')
    replit_domains = os.environ.get('REPLIT_DOMAINS')
    
    if replit_deployment:
        domain = os.environ.get('REPLIT_DEV_DOMAIN', '')
    elif replit_domains:
        domain = replit_domains.split(',')[0]
    else:
        # Fallback for local development
        domain = 'localhost:5000'
    
    # Use https for Replit domains, http for localhost
    protocol = 'https' if 'replit' in domain else 'http'
    return f"{protocol}://{domain}"

def create_checkout_session(project_id, investor_id, amount):
    """
    Create a Stripe checkout session for an investment.
    
    Args:
        project_id: The ID of the project being invested in
        investor_id: The ID of the investor
        amount: The investment amount in dollars
        
    Returns:
        The URL to redirect the user to for checkout
    """
    try:
        domain_url = get_domain()
        
        # Convert amount to cents for Stripe
        amount_cents = int(amount * 100)
        
        # Create a Stripe checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': f'Investment in Project #{project_id}',
                            'description': f'Investment of ${amount:.2f} in agricultural project',
                        },
                        'unit_amount': amount_cents,
                    },
                    'quantity': 1,
                },
            ],
            metadata={
                'project_id': project_id,
                'investor_id': investor_id,
                'amount': amount,
            },
            mode='payment',
            success_url=f"{domain_url}{url_for('investment_success')}?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{domain_url}{url_for('investment_cancel')}?project_id={project_id}",
        )
        return checkout_session.url
        
    except Exception as e:
        # Log the error
        print(f"Stripe Error: {str(e)}")
        return None

def retrieve_checkout_session(session_id):
    """
    Retrieve a checkout session by ID
    
    Args:
        session_id: The ID of the checkout session
        
    Returns:
        The checkout session object
    """
    try:
        return stripe.checkout.Session.retrieve(session_id)
    except Exception as e:
        # Log the error
        print(f"Stripe Error: {str(e)}")
        return None