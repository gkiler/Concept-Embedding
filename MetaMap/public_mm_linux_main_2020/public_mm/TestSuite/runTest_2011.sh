#!/bin/sh

# git rm *truncate* *contraction*

# AAs

# Usage: runTest_2011.sh [ -P -T ]
# Be sure to set METAMAP_TEST and METAMAP_PROD just below the comments
# Set METAMAP_PROD here!!
# and
# Set METAMAP_TEST here!!

announce() {
   echo $1
}

split_line(){
   LINE=$1
   FILENAME=`echo $LINE | cut -d'|' -f1`
   PRODFLAGS=`echo $LINE | cut -d'|' -f2`
   TESTFLAGS=`echo $LINE | cut -d'|' -f3`
   TITLE=`echo $LINE | cut -d'|' -f4`
   MODIFY=`echo $LINE | cut -d'|' -f5`

   # echo "LINE     = $LINE"
   # echo "FILENAME = $FILENAME"
   # echo "FLAGS    = $FLAGS"
   # echo "TITLE    = $TITLE"
   # echo "MODIFY   = $MODIFY"
}

test_filename_exists() {
   if [ ! -f $1 ]
   then
      echo ERROR: filename $1 does not exist.
      exit 1
   fi
}

change_metamap_text() {

   MODIFY=$1
   METAMAP=$2
   ORIG_FILENAME=$3
   NEW_FILENAME=$4

   if [ $MODIFY -eq 1 ]
   then
      echo "changing |$METAMAP|to|MetaMap|"

      sed -e "s#$METAMAP#MetaMap#g" $ORIG_FILENAME > $NEW_FILENAME
      /bin/rm -f $ORIG_FILENAME
   else
      /bin/mv -f $ORIG_FILENAME $NEW_FILENAME
   fi
}

diff_prod_test_files(){
   PROD_FILENAME=$1
   TEST_FILENAME=$2
   DIFF_FILENAME=$3

   if [ ! -f $PROD_FILENAME ]
   then
      echo "prod result file $PROD_FILENAME does not exist"
      exit 1
   elif [ ! -f $TEST_FILENAME ]
   then
      echo "test result file $TEST_FILENAME does not exist"
      exit 1
   else
      diff -b $PROD_FILENAME $TEST_FILENAME > $DIFF_FILENAME
      if [ -s $DIFF_FILENAME ]
      then
         cat $DIFF_FILENAME
      else
         echo DIFFS OK
      fi
   fi
}

run_test() {
   PRODorDEVL=$1
   PROGRAM=$2
   FLAGS=$3
   FILENAME=$4
   MODIFY=$5

   INFILE=$FILENAME.txt
   TMP_OUTFILE=$FILENAME.OUT
   OUTFILE=$FILENAME.${PRODorDEVL}

   echo $PROGRAM "$FLAGS" $INFILE $TMP_OUTFILE
   $PROGRAM "$FLAGS" $INFILE $TMP_OUTFILE # > /dev/null
   
   if [ ! -s $TMP_OUTFILE ]
   then
      echo ERROR: $TMP_OUTFILE is zero length.
      exit 1
   fi

   change_metamap_text $MODIFY "$PROGRAM" $TMP_OUTFILE $OUTFILE
}

RUN_PROD=0
RUN_TEST=0
PROGRAM=`basename $0`
USAGE='Usage: $PROGRAM [ -P -T ]'

while getopts TP option
do
   case $option
   in
   	P) RUN_PROD=1;;
   	T) RUN_TEST=1;;
        *) exit 1;
   esac
done

shift `expr $OPTIND - 1`
OPTIND=1

# The various tests are defined in lines such as the following:
# allow_overmatches|-o|-o|Overmatches|0|
# prefer_multiple_concepts|-Y|-Y|Prefer Multiple Concepts|0|
# ignore_word_order|-i|-i|Ignore Word Order|0|
#
#         FILENAME | PROD-FLAGS | DEVL-FLAGS | TITLE | MODIFY
#
# FILENAME:   The name of the file containing the text to be tested; assumes a ".txt" extension.
# PROD-FLAGS: The flags passed to Production MetaMap to run this test.
# DEVL-FLAGS: The flags passed to Development MetaMap to run this test.
# TITLE:      The name of the test (human readable).
# MODIFY:     0 or 1, depending on whether "MetaMap" should replace $METAMAP in the output file.
#             MODIFY should be 1 iff the test in question generates MMO or XML
# Unfortunately, the MODIFY feature needs some work...

# Set METAMAP_PROD here!!
# METAMAP_PROD is the current production version
METAMAP_PROD="metamap11 -V USAbase -Z 2011AB"

# Set METAMAP_TEST here!!
# METAMAP_TEST is the new development version to be tested
# METAMAP_TEST="SKRrun.11 ~/specialist/SKR/src/a.out.Linux -V USAbase -Z 2011AB --lexicon c"
METAMAP_TEST="SKRrun.11 $HOME/specialist/SKR/src/a.out.Linux --lexicon c -V USAbase -Z 2011AB"

echo "Start Time: `date`"
echo ""

if [ $RUN_PROD -eq 1 ]
then
  echo "MetaMap PROD: $METAMAP_PROD"
fi

if [ $RUN_TEST -eq 1 ]
then
   echo "MetaMap TEST: $METAMAP_TEST"
fi
echo ""

while read LINE
do
   echo Testing $LINE

   split_line "$LINE"

   test_filename_exists $FILENAME.txt

   if [ $RUN_PROD -eq 1 ]
   then
      echo running run_test prod "$METAMAP_PROD" "$PRODFLAGS" $FILENAME $MODIFY
      run_test prod "$METAMAP_PROD" "$PRODFLAGS" $FILENAME $MODIFY
   fi

   if [ $RUN_TEST -eq 1 ]
   then
      echo running run_test test "$METAMAP_TEST" "$TESTFLAGS" $FILENAME $MODIFY
      run_test test "$METAMAP_TEST" "$TESTFLAGS" $FILENAME $MODIFY
   fi

   echo "====================== DIFFS for $FILENAME ============================="
   diff_prod_test_files $FILENAME.prod $FILENAME.test $FILENAME.diff
   echo "====================== DIFFS END ==============================="
   echo ""

done << EOF
model_NLM|-V NLM|-V NLM|Model NLM|0|
model_USAbase|-V USAbase|-V USAbase|Model USAbase|0|
model_Base|-V Base|-V Base|Model Base|0|
UDA|--UDA UDAfile|--UDA UDAfile|UDA|0|
apostrophe_s_normal|||apostrophe_s_normal|0|
pruning|--prune 10|--prune 10|Pruning|0|
5zb|-zb --debug 5|-zb --debug 5|5zb Option|0|
EOT_marker|-E|-E|EOT marker|0|
MMI_fielded|-N|-N|MMI Fielded Output|0|
MMI_fielded_restrict_to_sources|-N -R MSH|-N -R MSH|MMI Fielded Output, Restrict to Sources|0|
NegEx_MMO|-q|-q|Simple NegEx Machine Output|1|
NegEx_XML|--XMLf|--XMLf|NegEx, XML format|1|
WSD_off_1|||Without WSD 1|0|
WSD_off_2|||Without WSD 2|0|
WSD_on_1|-y|-y|With WSD 1|0|
WSD_on_2|-y|-y|With WSD 2|0|
XML_format1|--XMLf1|--XMLf1|XML Format1|1|
XML_format|--XMLf|--XMLf|XML format|1|
XML_noformat1|--XMLn1|--XMLn1|XML noformat1|1|
XML_noformat|--XMLn|--XMLn|XML noformat|1|
allow_acros_abbrs_MMO|-aq|-aq|Acros and Abbrvs, MMO|1|
allow_concept_gaps_compute_all_mappings_2|-gb|-gb|Concept Gaps, All Mappings 2|0|
allow_concept_gaps_compute_all_mappings_debug5|-gb --debug 5|-gb --debug 5|Concept Gaps, All Mappings, Debug5|0|
allow_concept_gaps_compute_all_mappings_number_candidates|-gbn|-gbn|Concept Gaps, All Mappings, Number Candidates|0|
allow_concept_gaps_compute_all_mappings_show_CUIs|-gbI|-gbI|Concept Gaps, All Mappings, CUIs|0|
allow_concept_gaps_compute_all_mappings_show_syntax|-gbx|-gbx|Concept Gaps, All Mappings, Syntax|0|
allow_concept_gaps_compute_all_mappings|-gb|-gb|Concept Gaps, All Mappings|0|
allow_concept_gaps|-g|-g|Concept Gaps|0|
allow_overmatches|-o|-o|Overmatches|0|
best_mappings_only|||Normal Processing - Best Mappings Only|0|
compute_all_mappings_2|-b|-b|All Mappings 2|0|
compute_all_mappings_threshhold_900|-br 900|-br 900|All Mappings, Threshold=900|0|
compute_all_mappings|-b|-b|All Mappings|0|
exclude_sources|-e MSH|-e MSH|Exclude Sources|0|
fielded_MMI_ignore_word_order|-Ni|-Ni|Fielded MMI Output, Ignore Word Order|0|
head_scoring_1|-z|-z|Head Scoring 1|0|
head_scoring_2|-zi|-zi|Head Scoring 2|0|
hide_candidates|-c|-c|Hide Candidates|0|
hide_mappings|-m|-m|Hide Mappings|0|
ignore_word_order|-i|-i|Ignore Word Order|0|
ignore_word_order_term_processing|-zi|-zi|Ignore Word Order Term Processing|0|
MMO_CUIs|-qI|-qI|Machine Output, CUIs|1|
MMO|-q|-q|Machine Output|1|
no_hide_semantic_types|||No Hide Semantic Types|0|
non_standard_PMID|||Non-standard PMID|0|
plain_vanilla|||Plain Vanilla|0|
prefer_multiple_concepts|-Y|-Y|Prefer Multiple Concepts|0|
composite_phrases|-Q 4|-Q 4|Composite Phrases|0|
restrict_to_sources_XML|-R MSH --XMLf|-R MSH --XMLf|Restrict to Sources, XML format|1|
term_processing|-z|-z|Term processing|0|
yes_hide_semantic_types|-s|-s|Yes Hide Semantic Types|0|
MarineCorps|||Marine Corps|0|
EOF
