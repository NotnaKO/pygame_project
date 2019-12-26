from lessons import *


def end_screen(won):
    sp = []
    if won:
        intro_text = ["Вы победили"]
    else:
        intro_text = ["Вы проиграли"]
    intro_text.append("К уровням")
    fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 50)
    text_coord = [100, -170]
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord[1] += 230
        intro_rect.top = text_coord[1]
        text_coord[0] += 0
        intro_rect.x = text_coord[0]
        text_coord[0] += intro_rect.height
        sp.append(intro_rect)
        screen.blit(string_rendered, intro_rect)
    r = sp[1]
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN and r.collidepoint(event.pos):
                return display_lessons()
        pygame.display.flip()
        clock.tick(FPS)


