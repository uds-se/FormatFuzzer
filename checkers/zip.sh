yes | unzip -P '' -t out.zip >/dev/null 2>/dev/null
RETVAL=$?
[ $RETVAL = 0 -o $RETVAL = 1 ]
