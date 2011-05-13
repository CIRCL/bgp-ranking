#!/usr/bin/perl
#
# Takes as input IP address (one per line)
# and output the guessed IP location along with ASN origin and its description
# and the BGP Ranking of each ASN
#
#perl ip2asn.pl
# www.microsoft.com
# US;AS8075;MICROSOFT-CORP---MSN-AS-BLOCK - Microsoft Corp;65.55.12.249;8075,1.00036643769349,3/9
# 8.8.8.8
# US;AS15169;GOOGLE - Google Inc.;8.8.8.8;15169,1.00210796734234,4/9
# www.google.com
# US;AS15169;GOOGLE - Google Inc.;74.125.230.84;15169,1.00210796734234,4/9
# 4.4.4.4
# US;AS3356;LEVEL3 Level 3 Communications;4.4.4.4;3356,1.00000229260952,4/9
#
#
# This file is in the public domain.
#
# Alexandre Dulaunoy - http://github.com/adulau

# Gist here : 
# - https://gist.github.com/676046 (Alexandre Dulaunoy)
# - https://gist.github.com/953701 (Raphaël Vinot)

use strict;

use Net::Whois::RIS;
use IP::Country::Fast;
use Socket;
my $country = IP::Country::Fast->new();
$| = 1;

sub BGPRankingLookup {
    my $asn = shift;
    $asn =~ s/AS//g;

    my $bgpranking =
      IO::Socket::INET->new( PeerAddr => "pdns.circl.lu", PeerPort => 43 )
      or die();
    print $bgpranking $asn . "\n";
    my $x;
    while (<$bgpranking>) {
        $x = $x . $_;
    }
    chomp($x);
    return $x;

    $bgpranking->shutdown();
}
while (<STDIN>) {
    next if /^#/;
    chomp();
    my @v = split( / /, $_ );
    if ( !( $v[0] =~ /^(\d+\.){3}\d+$/ ) ) {
        my $ipn = inet_aton( $v[0] ) or next;
        $v[0] = inet_ntoa($ipn);
    }
    my $l = Net::Whois::RIS->new();
    $l->getIPInfo( $v[0] );
    my $origin = $l->getOrigin();
    print $country->inet_atocc( $v[0] ) . ";"
      . $origin . ";"
      . $l->getDescr() . ";"
      . $v[0] . ";"
      . BGPRankingLookup($origin) . "\n";
}
