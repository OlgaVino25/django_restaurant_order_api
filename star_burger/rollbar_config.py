import os


def init_rollbar():
    try:
        import rollbar
        from django.conf import settings

        if settings.ROLLBAR.get("enabled", False):
            rollbar.init(
                access_token=settings.ROLLBAR["access_token"],
                environment=settings.ROLLBAR["environment"],
                root=settings.ROLLBAR["root"],
                handler="blocking",
                locals={
                    "enabled": True,
                    "safe_list": ["request.META"],
                    "scrub_list": ["password", "secret", "token", "key"],
                },
            )
            return True
    except ImportError:
        pass
    return False
