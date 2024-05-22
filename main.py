from graph_api import read_and_send_emails
import logging

logger = logging.getLogger(__name__)

# Ensures on executable runs application
if __name__ == "__main__":
    logging.basicConfig(filename='myapp.log', level=logging.INFO)
    logger.info('Started Email Responses')
    read_and_send_emails()
    logger.info("Finished Email Responses")
