COMMAND = {
    "get_xvfb": "ps aux | grep '[x]vfb'",
    "get_hyna": "ps aux | grep '[h]yna.js' | grep -v 'xvfb'",
    "stop_process": "pkill -9 xvfb-run; pkill -9 Xvfb"
}