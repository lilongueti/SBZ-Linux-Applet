export DISPLAY=:0
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$(id -u)/bus
card_num=$(aplay -l | grep -m 1 Creative | grep -m 1 -Eo '[0-9]+' | head -n 1)
amixer -c $card_num sset Front on
amixer -c $card_num sset Master 1%-
amixer -c $card_num sset Front $(( 2 * $(amixer -c 2 sget Master | grep -oE '[0-9]{1,3}%' | grep -oE '[0-9]{1,3}')))%

notify-send "vol: $(amixer -c 2 sget Master | grep -oE '[0-9]{1,3}%')" -r 1996
