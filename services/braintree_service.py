import braintree
import os

from decimal import Decimal


class BraintreeSvc:

    def __init__(self):
        self.gateway = braintree.BraintreeGateway(
            braintree.Configuration(
                environment=braintree.Environment.Sandbox,
                merchant_id=os.getenv('BRAINTREE_MERCHANT_ID'),
                public_key=os.getenv('BRAINTREE_PUBLIC_KEY'),
                private_key=os.getenv('BRAINTREE_PRIVATE_KEY'),
            )
        )

    def submit_for_settlement(self, price: Decimal, papayment_method_nonce: str) -> bool:
        ret = self.gateway.transaction.sale({
            "amount": price,
            "payment_method_nonce": papayment_method_nonce,
            "options": {
                "submit_for_settlement": True
            },
        })

        if ret.is_success:
            settled_transaction = ret.transaction

            return settled_transaction.status in [
                braintree.Transaction.Status.SubmittedForSettlement,
                braintree.Transaction.Status.Settled,
            ]
        else:
            for error in ret.errors.deep_errors:
                print(f'{error.attribute} {error.code} {error.message}')

            raise ValueError(ret.message)


braintree_service = BraintreeSvc()
