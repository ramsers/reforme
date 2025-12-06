from django.db import migrations


def create_accounts_for_existing_users(apps, schema_editor):
    User = apps.get_model("user", "User")
    Account = apps.get_model("user", "Account")

    accounts_to_create = []
    for user in User.objects.all():
        if not Account.objects.filter(user=user).exists():
            accounts_to_create.append(Account(user=user, timezone="EST"))

    if accounts_to_create:
        Account.objects.bulk_create(accounts_to_create)


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0003_account"),
    ]

    operations = [
        migrations.RunPython(create_accounts_for_existing_users, migrations.RunPython.noop),
    ]
