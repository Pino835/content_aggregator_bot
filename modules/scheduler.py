"""
Logica de ejecucion periodica del bot mediante intervalos de tiempo.
"""

import time

import schedule


def iniciar_scheduler(funcion_tarea, intervalo_horas: float):
    """
    Programa la ejecucion de una funcion cada cierta cantidad de horas
    y queda corriendo indefinidamente hasta que se interrumpa el proceso.
    """
    schedule.every(intervalo_horas).hours.do(funcion_tarea)

    print(f"Scheduler iniciado: se ejecutara cada {intervalo_horas} horas. Presiona Ctrl+C para detener.")

    funcion_tarea()

    while True:
        schedule.run_pending()
        time.sleep(30)
