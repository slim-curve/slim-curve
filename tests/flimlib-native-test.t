  $ cp "$TESTDIR/../target/build/bin/flimlib-test" "$TESTDIR"/../test_files/* .

  $ (./flimlib-test ./test.json) | grep "TESTS RUN"
  84 TESTS RUN, 32 SUCCESSES, 52 FAILURES

  $ (./flimlib-test ./test.json) | grep "TESTS RUN"
  84 TESTS RUN, 32 SUCCESSES, 52 FAILURES

# greps changed json string from output as new reference
#  $ (./flimlib-test ./original.json) | grep '^[\s\S]*{' > ref.json

# finds FAILed tests from output
  $ (./flimlib-test ./ref.json) | perl -0777 -ne "while(m/\nTEST((.*\S.*)\n)+FAIL((.*\S.*)\n)+/g){print $&}"

