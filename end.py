from lessons import *


def end_screen(won, n):
    sp = []
    if won:
        intro_text = ["Вы победили"]
    else:
        intro_text = ["Вы проиграли"]
    intro_text.append("К уровням")
    intro_text.append("Главное меню")
    if won:
        intro_text.append('К следующему уровню')  # Пока не работает, сделаю после 2-3 релиза
    else:
        intro_text.append('Повторить попытку')
    fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 50)
    text_coord = [(100, 100), (120, 300), (95, 350)]
    if won:
        text_coord.append((65, 250))
    else:
        text_coord.append((75, 250))
    for line in range(len(intro_text)):
        string_rendered = font.render(intro_text[line], 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        intro_rect.top = text_coord[line][1]
        intro_rect.x = text_coord[line][0]
        sp.append(intro_rect)
        screen.blit(string_rendered, intro_rect)
    r = sp[1]  # Переход к уровням
    r1 = sp[2]  # Переход к главному меню
    r2 = sp[3]  # Переход к повтору или следующему уровню
    # Зависит от прохождения уровня
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if r.collidepoint(event.pos):
                    return display_lessons()
                if r1.collidepoint(event.pos):
                    return start_screen()
                if r2.collidepoint(event.pos):
                    return display_lessons(n)
        pygame.display.flip()
        clock.tick(FPS)
