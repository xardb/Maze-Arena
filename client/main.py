"""Maze Arena — терминальный клиент.

Точка входа. Пока реализован только каркас curses-приложения:
корректный запуск, отрисовка заставки и завершение по F10. 
"""

import curses


def draw_splash(screen):
    """Отрисовать стартовый экран-заставку."""
    screen.erase()
    height, width = screen.getmaxyx()

    title = "MAZE ARENA"
    hint = "Клиент запущен. Нажмите F10 для выхода."
    params = f"Параметры консоли: {width}, {height}"
    
    min_width, min_height = 100, 30
    not_enough_width_message = f"Сделайте терминал шире (минимум {min_width})"
    not_enough_height_message = f"Сделайте терминал выше (минимум {min_height})"
    params_y = height // 2 + 2

    if width < min_width:
        screen.addstr(height // 2 - 1, max(0, (width - len(not_enough_width_message)) // 2),
                      not_enough_width_message[:width - 1])
    if height < min_height:
        screen.addstr(height // 2, max(0, (width - len(not_enough_height_message)) // 2),
                      not_enough_height_message[:width - 1])
    if height >= min_height and width >= min_width:
        screen.addstr(height // 2 - 1, max(0, (width - len(title)) // 2), title)
        screen.addstr(height // 2 + 1, max(0, (width - len(hint)) // 2), hint)
    else:
        screen.addstr(params_y, max(0, (width - len(params)) // 2), params[:width - 1])

    screen.refresh()


def main(screen):
    """Главный цикл приложения.

    curses.wrapper вызывает эту функцию и гарантирует восстановление
    терминала при выходе, в том числе при исключении.
    """
    try:
        curses.curs_set(0)  # скрыть курсор
    except curses.error:
        pass

    screen.timeout(50)
    draw_splash(screen)

    while  screen.getch() != curses.KEY_F10:
        draw_splash(screen)


if __name__ == "__main__":
    curses.wrapper(main)
