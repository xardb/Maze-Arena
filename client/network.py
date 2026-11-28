"""Сетевой модуль TCP-клиента Maze Arena.

Отвечает только за обмен строками UTF-8 с сервером.
TCP не сохраняет границы сообщений, поэтому читаем поток
построчно через makefile, а не отдельными recv.

Чтение идёт в отдельном потоке, чтобы сеть не блокировала
отрисовку curses: полученные строки складываются в очередь,
главный цикл забирает их через poll().
"""

import queue
import socket
import threading


class TcpClient:
    """TCP-подключение к серверу с фоновым чтением строк."""

    def __init__(self, host, port, connect_timeout=5):
        self.sock = socket.create_connection((host, port), timeout=connect_timeout)
        self.sock.settimeout(None)  # дальше читаем без таймаута
        self.reader = self.sock.makefile("r", encoding="utf-8")
        self.lines = queue.Queue()
        self.is_closed = False
        self._thread = threading.Thread(target=self._read_loop, daemon=True)

    def start(self):
        """Запустить фоновое чтение строк от сервера."""
        self._thread.start()

    def _read_loop(self):
        """Читать строки до закрытия соединения."""
        try:
            for line in self.reader:
                self.lines.put(line.rstrip("\r\n"))
        except OSError:
            pass
        finally:
            self.is_closed = True

    def send_line(self, text):
        """Отправить одну строку, добавив перевод строки."""
        self.sock.sendall((text + "\n").encode("utf-8"))

    def poll(self, timeout=0):
        """Забрать строку из очереди.

        Без timeout — неблокирующе, вернёт None, если данных нет.
        С timeout — подождать указанное число секунд.
        """
        try:
            if timeout:
                return self.lines.get(timeout=timeout)
            return self.lines.get_nowait()
        except queue.Empty:
            return None

    def close(self):
        """Закрыть соединение."""
        try:
            self.sock.close()
        except OSError:
            pass
