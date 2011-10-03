from __future__ import print_function

import argparse
import sys

import boto

from postman import __version__


def cmd_send(args):
    ses = boto.connect_ses()
    msg = sys.stdin.read()
    # Verbosity lists all recipients instead of first
    if args.verbose:
        dests = ' '.join('post_to={0}'.format(d) for d in args.destinations)
    else:
        dests = 'post_to={0}'.format(args.destinations[0])
    details = 'post_from={0} {1}'.format(args.f, dests)
    try:
        result = ses.send_raw_email(msg, args.f, args.destinations)
        rbody = result.get("SendRawEmailResponse", {})
        msgid = rbody.get("SendRawEmailResult", {}).get("MessageId")
        reqid = rbody.get("ResponseMetadata", {}).get("RequestId")
        print("post_status=OK msgid={0} reqid={1} {2}".format(
            msgid, reqid, details))
    except boto.exception.BotoServerError as err:
        print('post_status=ERROR http_status={0} errmsg="{1}" errcode={2}'
                ' reqid={3} {4}'.format(err.status,
                                        err.error_message,
                                        err.error_code,
                                        err.request_id,
                                        details))
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
    fmt = "{0:<15} {1:<15} {2:<14}"
    print(fmt.format("SentLast24Hours", "Max24HourSend", "MaxSendRate"))
    fmt = "{0:<15.0f} {1:<15.0f} {2:<14.0f}"
    print(fmt.format(float(data["SentLast24Hours"]),
                     float(data["Max24HourSend"]),
                     float(data["MaxSendRate"])))


def cmd_show_stats(_args):
    ses = boto.connect_ses()
    data = ses.get_send_statistics()
    data = data["GetSendStatisticsResponse"]["GetSendStatisticsResult"]
    fmt = "{0:<20} {1:>10} {2:>8} {3:>7} {4:>7}"
    print(fmt.format('Timestamp', 'DeliveryAttempts',
                     'Rejects', 'Bounces', 'Complaints'))
    for datum in sorted(data["SendDataPoints"],
                        key=lambda x: x.get('Timestamp')):
        print(fmt.format(
            datum["Timestamp"],
            datum["DeliveryAttempts"],
            datum["Rejects"],
            datum["Bounces"],
            datum["Complaints"],
        ))


def cmd_delete_verified(args):
    ses = boto.connect_ses()
    for email in args.email:
        ses.delete_verified_email_address(email_address=email)
        print("Deleted {0}".format(email))


def main():
    parser = argparse.ArgumentParser(prog="postman", description="send an email via Amazon SES")
    parser.add_argument("--version", action="version", version="%%(prog)s %s" % __version__)
    parser.add_argument("--verbose", action="store_true")
    
    command_parsers = parser.add_subparsers(dest="command")
    
    # cmd: send
    parser_send = command_parsers.add_parser("send")
    parser_send.add_argument("-f",
        help="the address to send the message from, must be validated")
    parser_send.add_argument("destinations", metavar="TO", type=str, nargs="+",
        help="a list of email addresses to deliver message to")
    
    # cmd: verify
    parser_send = command_parsers.add_parser("verify")
    parser_send.add_argument("email", nargs="+",
        help="an email address to verify for sending from")
    
    # cmd: list_verified
    command_parsers.add_parser("list_verified")
    
    # cmd: show_quota
    command_parsers.add_parser("show_quota")
    
    # cmd: show_stats
    command_parsers.add_parser("show_stats")
    
    # cmd: delete_verified
    parser_delete = command_parsers.add_parser("delete_verified")
    parser_delete.add_argument("email", nargs="+",
        help="verified email addresses that will be deleted from verification list")
    
    args = parser.parse_args()
    
    {
        "send": cmd_send,
        "verify": cmd_verify,
        "list_verified": cmd_list_verified,
        "show_quota": cmd_show_quota,
        "show_stats": cmd_show_stats,
        "delete_verified": cmd_delete_verified
    }[args.command](args)
