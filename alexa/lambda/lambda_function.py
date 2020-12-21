import logging
import requests
import ask_sdk_core.utils as ask_utils

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Welcome to Honda Parking assistant. You can search for parking near a specific location, or I can mark your current location as a parking spot."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "I can help you find parking spots or mark your current location as a parking spot"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Thank you for using Honda Parking. Have a safe ride."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class SearchIntentHandler(AbstractRequestHandler):
    """Handler for Search Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("SearchIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        slots = handler_input.request_envelope.request.intent.slots
        location  = slots['Location'].value
        if location:
            url = "15.206.205.128/park/" + location
            response = requests.get(url)
            if response.status_code == 200:
                speak_output = response.text
            else:
                speak_output = "Sorry, I had trouble finding parking spots near" + location + ".";
        else:
            speak_output = "Sorry, I was unable to find parking spots near the requested location."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class MarkParkingSpotIntentHandler(AbstractRequestHandler):
    """Handler for Mark Parking Spot Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("MarkParkingSpotIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        
        #isAnAutomotiveEndpoint = handler_input.request_envelope.context.automotive;
        is_geo_location_enabled = handler_input.request_envelope.context.system.device.supported_interfaces.geolocation
        if is_geo_location_enabled :
            # get current lat and long
            geo_location_data = handler_input.request_envelope.context.geolocation
            coordinates = geo_location_data.coordinate
            if coordinates:
                # send API request with current lat and longitude
                url = "http://15.206.205.128/mark-parking-spot/"+str(coordinates.latitude_in_degrees) +","+str(coordinates.longitude_in_degrees) 
                response = requests.get(url)
                if response.status_code == 200:
                    speak_output = response.text
                else:
                    speak_output = "Sorry, I had trouble marking your current location as a parking spot"
            else:
                speak_output = "Sorry, I was unable to locate your current location, please try again later."
        else:
            speak_output = "Location Services are not enabled on your car."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class CatchAllExceptionHandler(AbstractExceptionHandler):
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(SearchIntentHandler())
sb.add_request_handler(MarkParkingSpotIntentHandler())

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()