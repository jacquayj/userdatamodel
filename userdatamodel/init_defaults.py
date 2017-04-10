from user import IdentityProvider
IDENTITY_PROVIDERS = ['google', 'itrust']
CLOUD_PROVIDERS = [
        {'name': 'cleversafe', 'service': 'storage'},
        {'name': 'ceph', 'service': 'storage'},
        {'name': 'AWS', 'service': 'general'}
]


def init_defaults(db):
    with db.session as s:
        for provider in IDENTITY_PROVIDERS:
            if not (
                    s.query(IdentityProvider)
                    .filter(IdentityProvider.name == provider)
                    .first()):
                provider = IdentityProvider(name=provider)
                s.add(provider)
        for provider in CLOUD_PROVIDERS:
            if not (
                    s.query(CloudProvider)
                    .filter(CloudProvider.name == provider['name'])
                    .first()):
                provider = CloudProvider(**provider)
                s.add(provider)
