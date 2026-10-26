"""Funktionen für E-Mails."""

# https://docs.python.org/3/library/smtplib.html
from email.message import EmailMessage
from email.utils import make_msgid
from smtplib import SMTP, SMTPServerDisconnected
from socket import gaierror
from typing import Final
from uuid import uuid4

from loguru import logger

from gast.config import mail_config, receiver, sender
lazy from gast.service.gast_dto import GastDTO

__all__ = ["send_mail"]

# WhatsApp-Nachricht durch PyWhatKit: https://github.com/Ankit404butfound/PyWhatKit
# knockknock fuer: SMS, Discord, Slack, Microsoft Teams, Telegram, ...


def send_mail(gast_dto: GastDTO) -> None:
    """Funktion, um eine E-Mail zu senden.

    :param gast_dto: Gast-Daten
    """
    logger.debug("{}", gast_dto)
    if not mail_config.enabled:
        logger.warning("send_mail: Der Mailserver ist deaktiviert")
        return

    # https://docs.python.org/3/library/email.examples.html
    msg: Final = EmailMessage()
    msg["From"] = sender
    msg["To"] = (receiver,)
    msg["Subject"] = f"Neuer Gast: ID={gast_dto.id}"
    # https://docs.python.org/3/library/email.utils.html#email.utils.make_msgid
    msg["Message-ID"] = make_msgid(idstring=str(uuid4()))

    msg.set_content(f"Neuer Gast: {gast_dto.nachname}")

    asparagus_cid: Final = make_msgid()
    msg.add_alternative(
        f"Neuer Gast: <b>{gast_dto.nachname}</b>".format(
            asparagus_cid=asparagus_cid[1:-1]
        ),
        subtype="html",
    )

    try:
        # https://docs.python.org/3/library/smtplib.html
        with SMTP(
            host=mail_config.host, port=mail_config.port, timeout=mail_config.timeout
        ) as smtp:
            # ggf. TLS verwenden und einloggen
            # smtp.starttls()
            # smtp.login("my_username", "my_password")
            logger.debug("msg={}", msg)
            smtp.send_message(msg)
    except ConnectionRefusedError:
        # https://docs.python.org/3/library/exceptions.html:
        # ConnectionRefusedError -> ConnectionError -> OSError
        # TODO https://github.com/python/cpython/issues/102414
        logger.warning("ConnectionRefusedError")
    except SMTPServerDisconnected:
        # z.B. bei Timeout
        # https://docs.python.org/3/library/smtplib.html
        # SMTPServerDisconnected -> SMTPException -> OSError
        logger.warning("SMTPServerDisconnected")
    except TimeoutError:
        logger.warning("TimeoutError beim Senden der E-Mail")
    except gaierror:
        # gai = getaddrinfo()  # NOSONAR
        logger.warning("socket.gaierror: Laeuft der Mailserver im virtuellen Netzwerk?")
