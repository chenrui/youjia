from app.utils.task import delay, context_loader


@delay
@context_loader
def delete_users(user_ids, **kwargs):
    pass
