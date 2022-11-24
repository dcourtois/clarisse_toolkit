# This class will be used to store all the data you need when running, and also serves as the event loop callback.
class EventLoop:
    def __init__(self):
        # for this example, we will track the default scene's light X translation.
        self.translate = ix.get_item("build://project/scene/light").attribute_exists("translate")
        self.translate_x = self.translate.get_double()

        # start the event loop
        self.running = True
        self.process_events()

    def process_events(self):
        # now get the current light's X translation, and if it changed, do stuff.
        x = self.translate.get_double()
        if x != self.translate_x:
            print("light moved to {}".format(x))
            self.translate_x = x

        # install the callback in the Clarisse event loop
        if self.running:
            # here we are telling Clarisse to only call us when at least 100 milliseconds have elapsed.
            # if we don't do that (leave this empty, which was the default on Clarisse SP9 and earlier) then
            # Clarisse will continuously call us, and this will result in 1 CPU core always being busy. You
            # can lower that number if you want more interactivity at the expanse of more CPU being used.
            ix.application.add_to_event_loop_single(self.process_events, 100)

# install the event loop if it's not already installed. This will start the loop and return immediately which
# allows this script to be used as a shelf.
# note that using the global `ix` module to store the EventLoop instance is very convenient because it will make
# the instance available to every other script in the same Clarisse session. See the end of this file for an
# example of why it's nice.
if not hasattr(ix, "_event_loop"):
    ix._event_loop = EventLoop()
else:
    # not necessary but I like knowing what happens :)
    print("Event loop already running.")


# since the event loop is now globally accessible, in another script (or shelf) you can then write the following
# piece of code to properly stop the event loop:
#
#     if hasattr(ix, "_event_loop"):
#         ix._event_loop.running = False
#         del ix._event_loop
#
