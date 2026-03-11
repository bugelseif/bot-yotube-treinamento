from botcity.maestro import *
from botcity.web import Browser, By, WebBot
from webdriver_manager.firefox import GeckoDriverManager

from log import logger

# Disable errors if we are not connected to Maestro
BotMaestroSDK.RAISE_NOT_CONNECTED = False


def main():
    # Runner passes the server url, the id of the task being executed,
    # the access token and the parameters that this task receives (when applicable).
    maestro = BotMaestroSDK.from_sys_args()
    ## Fetch the BotExecution with details from the task, including parameters
    execution = maestro.get_execution()

    print(f"Task ID is: {execution.task_id}")
    print(f"Task Parameters are: {execution.parameters}")


    bot = WebBot()

    # Configure whether or not to run on headless mode
    bot.headless = False

    # Uncomment to change the default Browser to Firefox
    bot.browser = Browser.FIREFOX

    # Uncomment to set the WebDriver path
    bot.driver_path = GeckoDriverManager().install()

    # Count variables
    sucesso = 0
    falha = 0

    logger.info("Execução do processo do Youtube iniciando")
    maestro.alert(
        task_id=execution.task_id,
        title="Execução começando",
        message="Execução do processo do Youtube iniciando",
        alert_type=AlertType.WARN
    )

    try:
        # Starting browser
        logger.info("Inicia o navegador")
        bot.browse(f"https://www.youtube.com/@botcity_br")
        
        # Search web element
        logger.info("Captura elemento")
        element = bot.find_elements(selector='//span[@class="yt-core-attributed-string yt-content-metadata-view-model__metadata-text yt-core-attributed-string--white-space-pre-wrap yt-core-attributed-string--link-inherit-color" and @role="text"]', by=By.XPATH)
        # Getting text property
        print(element[0].text)
        print(element[1].text)
        print(element[2].text)
        
        # Register the text infos in Orchestrator
        logger.info("Valores capturados...")
        logger.info(f"Nome do canal: {element[0].text}")
        logger.info(f"Numero de inscritos: {element[1].text}")
        logger.info(f"Numero de videos: {element[2].text}")

        # Save and register the file in Orchestrator
        logger.info("Salva captura de tela do navegador")
        bot.save_screenshot("log_tela_youtbe.png")

        logger.info("Registra captura no Orquestrador")
        maestro.post_artifact(
            task_id=execution.task_id,
            artifact_name="log_tela_youtbe.png",
            filepath="log_tela_youtbe.png"
        )

        # Finish task status - success
        logger.info("Define status e contagem de sucesso")
        sucesso += 1
        status=AutomationTaskFinishStatus.SUCCESS
        message="Tarefa finalizada com sucesso"

    except Exception as error:
        # Save and register error info
        logger.error("Salva captura de tela do erro")
        bot.save_screenshot("erro.png")
        
        logger.error("Salva captura de tela do erro")
        attachments = ['execution.log', 'erro.png']
        
        # Finish task status - error
        logger.error("Define status e contagem de erro")
        falha += 1
        status=AutomationTaskFinishStatus.FAILED
        message="Tarefa finalizada com falha"

        logger.error("Envia erro para o Orquestrador")
        maestro.error(
            task_id=execution.task_id, 
            exception=error, 
            screenshot="erro.png", 
            attachments=attachments
            )
        
    finally:
        # Wait 3 seconds before closing
        bot.wait(3000)

        # Finish and clean up the Web Browser
        # You MUST invoke the stop_browser to avoid
        # leaving instances of the webdriver open
        bot.stop_browser()

        maestro.alert(
            task_id=execution.task_id,
            title="Execução finalizou",
            message="Execução do processo do Youtube finalizado",
            alert_type=AlertType.WARN
        )

    # Register de finish task in Orquestrator
    logger.info("Finaliza a tarefa")
    maestro.finish_task(
        task_id=execution.task_id,
        status=status,
        message=message,
        total_items=1,
        processed_items=sucesso,
        failed_items=falha
    )

    logger.info("Envia arquivo de log")
    maestro.post_artifact(
        task_id=execution.task_id,
        artifact_name="execution.log",
        filepath="execution.log"
    )


def not_found(label):
    print(f"Element not found: {label}")


if __name__ == '__main__':
    main()
