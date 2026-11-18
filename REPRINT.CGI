#!/usr/local/bin/perl

require '/var/www/cgi-bin/JCODE.PL';
$| = 1;	 #force flsh the output buffer

#Name of cgi file
$script ="REPRINT.CGI";

#Name of data file
$csvfile = "/var/www/cgi-bin/REPRINT.CSV";
# The file encoding is euc-jp. Need Japanese font, e.g. IPA Gothic --> 
# http://moji.or.jp/wp-content/ipafont/IPAfont/ipag00303.zip

#Data style
#0=comma delimited text; 1=comma delimited text with double quotations [" "]; 
#2=delimited by angle brackets [< >])
$data_type = 0;

#Delimitation of keywords (0=half and full width spaces; 1= | [pipe])
$separate = 0;	

#html setting
$body = '<BODY>
<TT>';

#Title
$title = 'NONAME';

#Number of results per page
$pagelog = 10;

#Homepage
$home = '../INDEX.HTM';

#Setting of cloumns

#Colum names
@column_name = ('No. *', 'Author_Orig', 'Author_Pron', 
'Author_En', 'Year', 'Title_Orig', 'Title_En', 
'Journal_Orig', 'Journal_En', 'Volume', 'Number', 'Page_Start', 
'Page_End');

#Data attribution (1= text; 2=image; 3=URL) 
@column_type = ('1','1','1','1','1','1','1','1','1','1','1','1','1');

#Main body
if ($ENV{'HTTP_USER_AGENT'} !~ /MSIE/i) { $form_css = ""; }
&decode;
if ($separate) { $sepa = '|'; } else { $sepa = ' '; }

if ($mode eq "find") { &find; }

#html display
&header;
	print <<"EOF";
<TT>
Geography Reprint Database ; 
Certos Acontecimentos Sao Predestinados A Acontecer 
<FORM METHOD="post" ACTION="$script">
   <INPUT TYPE="text" NAME="keyword" size="30" VALUE="$h_word$sepa" $form_css>
   <INPUT TYPE="submit" NAME="submit" VALUE="Submit" $form_css>
   <INPUT TYPE="hidden" NAME="mode" VALUE="find">
</FORM>
EOF
&footer;

#Search
sub find {
	if ($FORM{'keyword'} ne "") {
	$keyword =~ s/\t/ /g;
	if (!$separate) {
		&jcode'convert(*keyword, "euc");

		#Full width space -> half width spaces
		$keyword =~ s/([\x80-\xff][\x80-\xff]|[\x00-\x7f])/
		($1 eq "\xa1\xa1") ? " " : $1/eg;
	}
	&jcode'convert(*keyword,'euc');
	$h_word = $keyword;
	$keyword =~ s/(\W)/\\$1/g;    #insert "\" between Japanese letters
	if ($separate) {
		@pairs = split(/\\\|+/,$keyword);
	} else {
		@pairs = split(/\\\s+/,$keyword);
	}
	open(IN,"$csvfile") || &error("Database Error");
	@lines = <IN>;
	close(IN);
	foreach $line (@lines) {
		$flag = 0;
		&jcode'convert(*line,'euc');
		foreach $pair (@pairs) {
		if ($line =~ /$pair/i) { $flag++; }
		}
		if ($flag == @pairs) { push(@new,$line); }
	}
	$count = @new;
	}

#Display result
	&header;
	if (!@new) {
	print "<BR>No result for <B><U> $h_word </U></B><BR> 
	<BR> <BR> \n";
	} else {
	if ($FORM{'page'} eq '') { $page = 0; }
	else { $page = $FORM{'page'}; }

#Display page number
	$end_data = @new - 1;
	$page_end = $page + ($pagelog - 1);
	$p = int(@new / $pagelog);
	if (@new % $pagelog) { $p++; }
	if ($page_end >= $end_data) { $page_end = $end_data; }
	$str = $page + 1;
	$end = $page_end + 1;
	$next_line = $page_end + 1;

#Display result (above table)
	&pagechg_1;

#Display column attribute
	print <<"EOF";
	<TABLE BORDER="1">
	<TR>
EOF
	foreach (0 .. $#column_name) {
		print "<TD>$column_name[$_]</TD>\n";
	}
	print "</TR>\n";

	foreach $data ($page .. $page_end) {
		$data = $new[$data];
		&jcode'convert(*data,'euc');
		if ($data_type eq "1") {
		$data =~ s/^\"//g;
		$data =~ s/\"$//g;
		@col_name = split(/\"\,\"/,$data);
		} elsif ($data_type eq "2") {
		@col_name = split(/<>/,$data);
		} else {
		@col_name = split(/\,/,$data);
		}

		print "<TR>\n";
		foreach (0 .. $#column_name) {
		if ([$_]) { $w = "nowrap"; }
		else { $w =""; }
		if ($r_align[$_] eq "1") { $r = " align=\"center\""; }
		elsif ($r_align[$_] eq "2") { $r = " align=\"right\""; }
		else { $r = ""; }
		&col_type;
		print "<TD>$col_name[$_]</TD>\n";
		}
		print "</TR>\n";
	}

	print "</TABLE></TD></TR></TABLE><P>\n";

#Display result (under table)
	&pagechg_2;
	print <<"EOF";
EOF
	}
	&footer;
exit;
}

#Header
sub header {
print "CONTENT-TYPE: TEXT/HTML\n\n";
print <<"EOF";
<HTML>
<HEAD>
   <TITLE>$title</TITLE>
   <META NAME="AUTHOR" CONTENT="T. Nihei">
   <META HTTP-EQUIV="CONTENT-TYPE" CONTENT="TEXT/HTML; CHARSET=EUC-JP">
   <META NAME="build VER 1" CONTENT="2004.4.29">
   <META NAME="build VER 2" CONTENT="2005.5.1">
   <META NAME="1ST URL" CONTENT="http://deanmac.hibun.tsukuba.ac.jp/cgi/journal.html">
   <META NAME="2ND URL" CONTENT="http://geo.let.hokudai.ac.jp/cgi-bin/journal2.cgi">
</HEAD>
$body
EOF
}

#Footer
sub footer {
print <<"EOF";
<!-- <A HREF=../CGI/JOURNAL.HTM>Search In Detail</A> -->
</TT>
</BODY>
</HTML>
EOF
}

#Display errata
sub error {
	print "CONTENT-TYPE: TEXT/HTML\n\n";
	print "<HTML><HEAD><TITLE>$title</TITLE></HEAD>\n";
	print "$body\n";
	print "<H3>$_[0]</H3>\n";
	print "<A HREF=\"javascript:history.back()\">Back</A> \n";
	print "</TT></BODY></HTML>\n";
	exit;
}

#Processing database
sub decode {
	if ($ENV{'REQUEST_METHOD'} eq "POST") {
	if ($ENV{'CONTENT_LENGTH'} > 51200) { &error("Error"); }
	read(STDIN, $buffer, $ENV{'CONTENT_LENGTH'});
	} else { $buffer = $ENV{'QUERY_STRING'}; }

	@pairs = split(/&/,$buffer);
	foreach $pair (@pairs) {
	($name, $value) = split(/=/, $pair);
	$value =~ tr/+/ /;
	$value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;

	#Conversion text encoding
	#&jcode'convert(*value,'euc');

	#Tag processing
	$value =~ s/\"/&quot;/g;
	$value =~ s/\</&lt;/g;
	$value =~ s/\>/&gt;/g;
	$value =~ s/\n//g;
	$value =~ s/\r//g;
	$value =~ s/\t//g;
	$value =~ s/\,//g;

	$FORM{$name} = $value;
	}

	$keyword = $FORM{'keyword'};
	$mode = $FORM{'mode'};
}

#Display result 1
sub pagechg_1 {
	$pflag = 0;

	#Remove "\" and seach again
	$keyword =~ s/\\//g;
	if ($separate) {
	@words = split(/\|/,$h_word);
	} else {
	@words = split(/\s/,$h_word);
	}
	print "Results <B>$str</B> - <B>$end</B> of <B>$count</B> records for '<B>";
	
	foreach (@words) {
	$pflag++;

	print "$_";
	if ($pflag ne @words) {
		print "</B>' and '<B>";
	}
	}
	print "</B>' <BR><BR> ";

}

#Display result 2
sub pagechg_2 {
	$pflag = 0;

	#Remove "\" and seach again
	$keyword =~ s/\\//g;
	if ($separate) {
	@words = split(/\|/,$h_word);
	} else {
	@words = split(/\s/,$h_word);
	}
	print "Result : ";
	foreach (0 .. $p - 1 ) {
	$i = $_ * $pagelog;
	$_++;
	if ($page ne $i) {
		if ($_ < 11) {
		print "<A HREF=\"$script?mode=find&keyword=$h_word&page=$i\">$_</A>\n";
		} elsif (!($_ % 10)) {
		print "\.\. <A HREF=\"$script?mode=find&keyword=$h_word&page=$i\">$_</A>\n";
		}
	} else {
		if ($_ < 11) {
		print "<B>$_</B>\n";
	} elsif (!($_ % 10)) {
		print "\.\. <B>$_</B>\n";
		} elsif (($_ % 10) eq 9) {
		print "\.\. <B>$_</B>\n";
		} elsif (($_ % 10) eq 1) {
		print "<B>$_</B>\n";
		} elsif ($_ % 10) {
		print "\.\. <B>$_</B>\n";
		} else {
		print "<B>$_</B>\n";
		}
	}
	}
	print" ";
	
	if ($page_end ne $end_data) {
  print "... <A HREF=\"$script?mode=find&keyword=$h_word&page=$next_line\">next $pagelog</A>\n";
	
	 }
  print "<BR> <BR> \n";
  print "* PDF file available ; <BR> \n";
  print "1234 --> HTTP://2242.MOOO.COM/REP/1234.PDF <BR>\n";
  print " JS --> See J-STAGE. \n";
}

#Column name
sub col_type {
	if ($column_type[$_] eq "2") {
	$col_name[$_] = "<img src=\"$col_name[$_]\">";
	} elsif ($column_type[$_] eq "3") {
	$col_name[$_] =~ s/([^=^\"]|^)(http\:[\w\.\~\-\/\?\&\+\=\:\@\%\;\#]+)/$1<a href=\"$2\" target=\"_top\">URL<\/a>/g;
	}
}

