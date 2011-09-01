from __future__ import print_function

import argparse
import sys

import boto

from postman import __version__


def cmd_send(args):
    ses = boto.connect_ses()
    msg = sys.stdin.read()
    details = 'ses_from={0} {1}'.format(args.f, ' '.join(
        'ses_to=' + d for d in args.destinations))
    if args.f == "MAILER-DAEMON":
        print("ses_status=IGNORE {0}".format(details))
    else:
        try:
            result = ses.send_raw_email(msg, args.f, args.destinations)
            if result.get("SendRawEmailResponse", {})\
               .get("SendRawEmailResult", {})\
               .get("MessageId"):
                print("ses_status=OK {0}".format(details))
            else:
                print("ses_status=NOTSENT {0} {1}".format(details, result))
                sys.exit(1)
        except boto.exception.BotoServerError as err:
            print('ses_status=ERROR status={0} reason="{1}"'
                  ' message="{2}" code={3} {4}'.format(
                      err.status, err.reason, err.error_message,
                      err.error_code, details))
            sys.exit(1)


def cmd_verify(args):
    ses = boto.connect_ses()
    for email in args.email:
        ses.verify_email_address(email)
        print("Verification for {0} sent.".format(email))


def cmd_list_verified(_args):
    ses = boto.connect_ses()
    addresses = ses.list_verified_email_addresses()
    addresses = addresses["ListVerifiedEmailAddressesResponse"]
    addresses = addresses["ListVerifiedEmailAddressesResult"]
    addresses = addresses["VerifiedEmailAddresses"]
    if not addresses:
        print("No addresses are verified on this account.")
        return
    for address in sorted(addresses):
        print(address)


def cmd_show_quota(_args):
    ses = boto.connect_ses()
    data = ses.get_send_quota()["GetSendQuotaResponse"]["GetSendQuotaResult"]
    print("Max 24 Hour Send: {0}".format(data["Max24HourSend"]))
    print("Sent Last 24 Hours: {0}".format(data["SentLast24Hours"]))
    print("Max Send Rate: {0}".format(data["MaxSendRate"]))


def cmd_show_stats(_args):
    ses = boto.connect_ses()
    data = ses.get_send_statistics()
    data = data["GetSendStatisticsResponse"]["GetSendStatisticsResult"]
    fmt = "{0:>20} {1:>10} {2:>8} {3:>7} {4:>7}"
    print(fmt.format('Timestamp', 'Complaints', 'Attempts', 'Bounces', 'Rejects'))
    for datum in sorted(data["SendDataPoints"], key=lambda x:x.get('Timestamp')):
        print(fmt.format(datum["Timestamp"],
                         datum["Complaints"],
                         datum["DeliveryAttempts"],
                         datum["Bounces"],
                         datum["Rejects"]))


def cmd_delete_verified(args):
    ses = boto.connect_ses()
    for email in args.email:
        ses.delete_verified_email_address(email_address=email)
        print("Deleted {0}".format(email))


def main():
    parser = argparse.ArgumentParser(
        prog="postman", description="send an email via Amazon SES")
    parser.add_argument("--version", action="version",
                        version="postman " + __version__)

    commands = parser.add_subparsers(dest="command")

    parser_send = commands.add_parser("send")
    parser_send.add_argument("-f",
        help="the address to send the message from, must be validated")
    parser_send.add_argument("destinations", metavar="TO", nargs="+",
        help="a list of email addresses to deliver message to")

    parser_verify = commands.add_parser("verify")
    parser_verify.add_argument("email", nargs="+",
        help="an email address to verify for sending from")

    commands.add_parser("list_verified")
    commands.add_parser("show_quota")
    commands.add_parser("show_stats")

    parser_delete = commands.add_parser("delete_verified")
    parser_delete.add_argument("email", nargs="+",
        help="verified email addresses to deleted from verification list")

    cmdmap = {
        "send": cmd_send,
        "verify": cmd_verify,
        "list_verified": cmd_list_verified,
        "show_quota": cmd_show_quota,
        "show_stats": cmd_show_stats,
        "delete_verified": cmd_delete_verified
    }
    args = parser.parse_args()
    cmdmap[args.command](args)
