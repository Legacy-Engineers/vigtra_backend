import graphene


class SiteConfigType(graphene.ObjectType):
    name = graphene.String()
    logo = graphene.String()
    description = graphene.String()
    contact_email = graphene.String()
    contact_phone = graphene.String()
    contact_address = graphene.String()
    contact_website = graphene.String()
