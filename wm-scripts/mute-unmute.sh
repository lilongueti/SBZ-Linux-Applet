activo=$(amixer -c 2 sget Master | grep "\[off\]")
echo $activo
if [[ -z $activo ]]; then
amixer -c 2 sset Master off
else
amixer -c 2 sset Master on
amixer -c 2 sset Front on
fi
