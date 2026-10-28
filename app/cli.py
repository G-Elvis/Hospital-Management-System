from datetime import date

import click

from app.domain.exceptions import DomainError
from app.domain.user import Role


def register_cli(app):
    @app.cli.command("seed-admin")
    @click.option("--username", envvar="ADMIN_USERNAME", default="admin", show_default=True)
    @click.option("--password", envvar="ADMIN_PASSWORD", required=True,
                  help="At least 8 characters. Never commit this value.")
    def seed_admin(username, password):
        """Create the first administrator account."""
        try:
            app.extensions["admin_service"].create_user(username, password, Role.ADMIN)
        except DomainError as err:
            raise click.ClickException(str(err)) from err
        click.echo(f"Administrator '{username}' created.")

    @app.cli.command("seed-demo")
    @click.option("--password", envvar="DEMO_PASSWORD", default="DemoPass123!",
                  show_default=True, help="Shared password for the demo accounts.")
    def seed_demo(password):
        """Load demo accounts and patients. FOR DEMOS ONLY - never use in production."""
        admin, patients = app.extensions["admin_service"], app.extensions["patient_service"]
        for username, role in (("admin", Role.ADMIN), ("reception", Role.RECEPTIONIST),
                               ("dr_ann", Role.DOCTOR), ("dr_ben", Role.DOCTOR)):
            try:
                admin.create_user(username, password, role)
            except DomainError:
                pass                                    # already exists
        for name, dob, gender, phone in (
                ("Jane Doe", date(1990, 5, 1), "Female", "0712345678"),
                ("John Smith", date(1985, 11, 23), "Male", "0723456789"),
                ("Amina Yusuf", date(2001, 2, 14), "Female", "0734567890")):
            try:
                patients.register(name, dob, gender, phone)
            except DomainError:
                pass
        click.echo(f"Demo data ready. Accounts: admin, reception, dr_ann, dr_ben "
                   f"(password: {password})")
