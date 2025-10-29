import dataclasses


@dataclasses.dataclass
class IntegratorPaymentMethod:
    name: str
    logo: str
    payment_type: str
    description: str


@dataclasses.dataclass
class IntegratorDefinition:
    name: str
    code: str
    description: str
    module: str
    configuration: dict
    payment_methods: list[IntegratorPaymentMethod]


INTEGRATORS = [
    IntegratorDefinition(
        name="Modem Pay",
        code="modem-pay",
        description="This is a payment gateway",
        module="modules.payment_gateway.modem_pay",
        configuration={
            "sample_key": "sample_value",
        },
        payment_methods=[
            IntegratorPaymentMethod(
                name="Visa Card",
                description="This is the description",
                logo="ssasasasasasasasa",
                payment_type="card",
            )
        ],
    )
]
