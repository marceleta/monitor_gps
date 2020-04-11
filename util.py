import logging

logging.basicConfig(level=logging.INFO, filename='monitoramento.log', filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d/%m/%Y %I:%M')


class Log:

    @staticmethod
    def debug(mensagem):
        logging.debug(mensagem)

    @staticmethod
    def info(mensagem):
        logging.info(mensagem)

    @staticmethod
    def warning(mensagem):
        logging.warning(mensagem)

    @staticmethod
    def error(mensagem):
        logging.error(mensagem)
