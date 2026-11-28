"""Maze Arena — терминальный клиент.

Точка входа: параметры подключения, ввод имени, TCP-подключение,
регистрация на сервере и главный curses-цикл.

Пока полученные от сервера строки показываются как есть, чтобы проверить обмен.
"""

import argparse
import curses
import re
from collections import deque

from network import TcpClient

NAME_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,16}$")  # ник на входе
MAX_LOG_LINES = 50


def parse_args():
    parser = argparse.ArgumentParser(description="TUI-клиент Maze Arena")
    parser.add_argument("--host", default="127.0.0.1", help="адрес сервера")
    parser.add_argument("--port", type=int, default=5000, help="порт сервера")
    return parser.parse_args()


def ask_name():
    """Спросить имя игрока до входа в curses."""
    while True:
        name = input("Введите имя игрока: ").strip()
        if NAME_PATTERN.match(name):
            return name
        print("Имя: 1-16 символов, латинские буквы, цифры, _ и -")


def connect_and_join(host, port, name):
    """Подключиться и зарегистрироваться на сервере.

    Возвращает TcpClient при успехе, иначе None.
    """
    print(f"Подключение к {host}:{port} ...")
    try:
        client = TcpClient(host, port)
    except OSError as exc:
        print(f"Не удалось подключиться: {exc}")
        return None
    client.start()

    client.send_line(f"подключись как игрок {name}")
    reply = client.poll(timeout=5)

    if reply is None:
        print("Сервер не ответил на регистрацию")
    elif reply.startswith("Подключён"):
        print(reply)
        return client
    else:
        print(f"Сервер отклонил подключение: {reply}")

    client.close()
    return None


def draw_screen(screen, name, address, received, closed):
    """Отрисовать экран: заставка, статус подключения и журнал строк."""
    screen.erase()
    height, width = screen.getmaxyx()

    min_width, min_height = 100, 30
    not_enough_width_message = f"Сделайте терминал шире (минимум {min_width})"
    not_enough_height_message = f"Сделайте терминал выше (минимум {min_height})"

    if width < min_width:
        screen.addstr(height // 2 - 1, max(0, (width - len(not_enough_width_message)) // 2),
                      not_enough_width_message[:width - 1])
    if height < min_height:
        screen.addstr(height // 2, max(0, (width - len(not_enough_height_message)) // 2),
                      not_enough_height_message[:width - 1])
    if height >= min_height and width >= min_width:
        title = "MAZE ARENA"
        status = f"Игрок: {name}   Сервер: {address}"
        hint = "F10 — выход"

        screen.addstr(1, max(0, (width - len(title)) // 2), title)
        screen.addstr(2, max(0, (width - len(status)) // 2), status)
        screen.addstr(3, max(0, (width - len(hint)) // 2), hint)

        if closed:
            message = "Соединение с сервером закрыто"
            screen.addstr(5, max(0, (width - len(message)) // 2), message)

        # пока состояние не разбирается, показываем сырые строки от сервера
        screen.addstr(7, 2, "Последние сообщения сервера:")
        visible = list(received)[-(height - 10):]
        for index, line in enumerate(visible):
            screen.addstr(8 + index, 2, line[:width - 4])
    else:
        params = f"Параметры консоли: {width}, {height}"
        params_y = height // 2 + 2
        screen.addstr(params_y, max(0, (width - len(params)) // 2), params[:width - 1])

    screen.refresh()


def main(screen, client, name, address):
    """Главный цикл: читать сеть без блокировки и перерисовывать экран."""
    try:
        curses.curs_set(0)  # скрыть курсор
    except curses.error:
        pass

    screen.timeout(50)  # getch ждёт максимум 50 мс, цикл не блокируется
    received = deque(maxlen=MAX_LOG_LINES)
    closed = False

    while True:
        # забрать все строки, накопившиеся с прошлой итерации
        while True:
            line = client.poll()
            if line is None:
                break
            received.append(line)

        if client.is_closed and not closed:
            closed = True

        draw_screen(screen, name, address, received, closed)

        if screen.getch() == curses.KEY_F10:
            break

    # вежливый выход, если соединение ещё живо
    if not closed:
        try:
            client.send_line("выйди из игры")
        except OSError:
            pass
    client.close()


if __name__ == "__main__":
    args = parse_args()
    name = ask_name()
    client = connect_and_join(args.host, args.port, name)
    if client is not None:
        address = f"{args.host}:{args.port}"
        try:
            curses.wrapper(main, client, name, address)
        except KeyboardInterrupt:
            client.close()
