pdfinfo out.pdf 2>&1 | grep Error >/dev/null
RETVAL=$?
[ $RETVAL = 1 ]
