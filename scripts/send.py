from datetime import datetime
import fxsignal
import yaml
import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    handlers=[logging.FileHandler("./logs/fxsignal.log"), logging.StreamHandler()])

def send_fleep_message(config):
    fleep = fxsignal.Fleep(config['fleep']['token'], 'ForexAdvisor')
    # data = pd.DataFrame()
    fleep.send("Test messge")


def run():
    with open('./scripts/config.yaml') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    send_fleep_message(config)

if __name__ == '__main__':
    run()
