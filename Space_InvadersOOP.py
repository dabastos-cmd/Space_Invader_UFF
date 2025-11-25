from pplay.window import * # type: ignore
from pplay.sprite import * # type: ignore
from pplay.gameimage import * # type: ignore
from pplay.sound import * # type: ignore
from datetime import datetime
import random

random.seed()
clock = pygame.time.Clock()

janela = Window(900,900)
janela.set_title("Menu - Space Invaders")

teclado = janela.get_keyboard()
mouse = janela.get_mouse()
background_color = [0, 0, 0]

img_enemy1 = "img/enemy1.png"
img_tiro = "img/Tiro.png"
img_player_model = "img/player_model.png"
img_botao = "img/botao_menu.png"
img_botao_pressed = "img/botao_menu_pressed.png"

pontuacao_atual = 0
dificulty = 2
lista_de_tiros_inimigos = []
matriz_de_inimigos = []
Col = 10
Lin = 5

class Tiro(Sprite):
    def __init__(self, image_file, frames=1):
        super().__init__(image_file, frames)

    def move(self,speed):
        self.move_y(speed)

class Player(Sprite):
    def __init__(self,vidas = 3,lista = [], speed_player = 300, image_file = img_player_model, frames=2):
        super().__init__(image_file, frames)
        self.speed = speed_player
        self.x = janela.width//2 - self.width//2
        self.y = janela.width - self.height
        self.lista_de_tiros_player = lista
        self.vidas = vidas

    def shoot(self):
        tiro = Tiro(img_tiro)
        tiro.x = self.x + self.width//2
        tiro.y = self.y
        self.lista_de_tiros_player.append(tiro)

    def clean_tiros(self):
        self.lista_de_tiros_player.clear()

    def position_player_tiros(self):
        for _ in self.lista_de_tiros_player:
            _.move(-150*janela.delta_time())

    def draw_player_tiros(self):
        for _ in self.lista_de_tiros_player:
            _.draw()

    def lost_life(self):
        self.vidas -= 1

    def delete_shot(self,index):
        del self.lista_de_tiros_player[index]

class Enemy(Sprite):
    def __init__(self,direction = -1,speed_enemy = 750, image_file = img_enemy1, frames=1):
        super().__init__(image_file, frames)
        self.speed = speed_enemy*janela.delta_time()
        self.direction = direction
        
    def shoot(self):
        tiro = Tiro(img_tiro,1)
        tiro.x = self.x + self.width//2
        tiro.y = self.y + self.height//2
        lista_de_tiros_inimigos.append(tiro)

    def position_enemy_tiros(self):
        for _ in lista_de_tiros_inimigos:
            _.move(150*janela.delta_time())

    def draw_enemy_tiros(self):
        for _ in lista_de_tiros_inimigos:
            _.draw()

    def check_collision(self,lis): #lis deve ser o atributo lista_de_tiros_player de uma instância player() inicialmente
        for j in range(len(lis)):
            for i in range(len(matriz_de_inimigos)):
                if matriz_de_inimigos[i].collided(lis[j]):
                    matriz_de_inimigos.pop(i)



botao_jogar = GameImage(img_botao)
botao_dif = GameImage(img_botao)
botao_ranking = GameImage(img_botao)
botao_sair = GameImage(img_botao)
botao_facil = GameImage(img_botao)
botao_medio = GameImage(img_botao)
botao_dificil = GameImage(img_botao)

botao_menu_x = janela.width/2 - botao_jogar.width/2

botao_jogar.set_position(botao_menu_x,100)
botao_dif.set_position(botao_menu_x,300)
botao_ranking.set_position(botao_menu_x,500)
botao_sair.set_position(botao_menu_x,700)

def aux_funtion_sorted(elemento_matriz_ranking):
    extraction = ""
    extracted = False
    for i in range(len(elemento_matriz_ranking)-1):
        if elemento_matriz_ranking[i] == "-" and elemento_matriz_ranking[i+1] == " " and not extracted:
            i += 2
            while elemento_matriz_ranking[i] != " ":
                extraction += elemento_matriz_ranking[i]
                i += 1
            extracted = True
    return int(extraction)




def dificulty_step(Col,Lin,dificuldade):
    if dificuldade == 2:
        Col = 10
        Lin = 5
    elif dificuldade == 3:
        Col = 12
        Lin = 6
    return Col, Lin, dificuldade

def generate_enemy_matrix():
    for j in range(Lin+1):
        lista_de_inimigos = []
        for i in range(1,Col+1):
            enem = Enemy()
            enem.x = int(janela.width - enem.width*1.5*i)
            enem.y = int(enem.height*1.5*j)
            lista_de_inimigos.append(enem)
        matriz_de_inimigos.append(lista_de_inimigos.copy())

def gameloop():
    tiro_delay_player = 0
    tiro_delay_enemy = 0
    tempo_invencivel = 2
    move_delay = 0
    Anim_Acc = 0
    Switch_timer = True
    pont = 0

    player = Player()
    player.set_sequence_time(0,1,300)
    enemy = Enemy() #inimigo invisível para referência
    generate_enemy_matrix()

    while True:
        if player.vidas < 1:
            player.clean_tiros()
            lista_de_tiros_inimigos.clear()
            matriz_de_inimigos.clear()
            del player
            return pont

        #limpo linhas da matriz que estão vazias para evitar erros de indexação(gerar mais inimigos mais rapidos )
        if matriz_de_inimigos == []:
            global Col, Lin,dificulty
            player.clean_tiros()
            Col,Lin,dificulty = dificulty_step(Col,Lin,dificulty+1)[0],dificulty_step(Col,Lin,dificulty+1)[1],dificulty_step(Col,Lin,dificulty+1)[2]
            generate_enemy_matrix()
        
        #atiro com a matriz de inimigos aleatóriamente
        if len(lista_de_tiros_inimigos) < 2 and tiro_delay_enemy > 1+(random.randrange(0,3)):
            linha = random.choice(matriz_de_inimigos)
            escolhido = random.choice(linha)
            escolhido.shoot()
            tiro_delay_enemy = 0

        if teclado.key_pressed("SPACE") and tiro_delay_player > 0.5*dificulty: # pyright: ignore[reportOperatorIssue]
            player.shoot()
            tiro_delay_player = 0

        #movimento o player e seto barreiras
        player.move_key_x(player.speed*janela.delta_time()/dificulty) # pyright: ignore[reportOperatorIssue]
        if player.x + player.width >= janela.width:
            player.x = janela.width - player.width
        elif player.x <= 0:
            player.x = 0

        #checo se algum tiro saiu da tela e apago eles
        for _ in player.lista_de_tiros_player:
            if _.x > janela.width or _.x < 0 or _.y > janela.height or _.y < 0:
                del player.lista_de_tiros_player[player.lista_de_tiros_player.index(_)]
        for _ in lista_de_tiros_inimigos:
            if _.x > janela.width or _.x < 0 or _.y > janela.height or _.y < 0:
                del lista_de_tiros_inimigos[lista_de_tiros_inimigos.index(_)]

        #posiciono tiros do player
        player.position_player_tiros()
        #posiciono tiros da lista de tiros inimigos
        enemy.position_enemy_tiros()

        #checo a colisão de tiros do player com inimigos da matriz de inimigos
        for j in matriz_de_inimigos:
            for _ in j:
                for i in player.lista_de_tiros_player:
                    if i.collided(_):
                        del matriz_de_inimigos[matriz_de_inimigos.index(j)][j.index(_)]
                        player.delete_shot(player.lista_de_tiros_player.index(i))
                        pont += 1

        #checo a colisão de tiros da lista de tiros de inimigos com o player(implementar invencibilidade pro 2 segundos)
        for i in lista_de_tiros_inimigos:
            if i.collided(player) and tempo_invencivel >= 2:
                player.lost_life()
                del lista_de_tiros_inimigos[lista_de_tiros_inimigos.index(i)]
                player.x = janela.width//2 - player.width//2
                tempo_invencivel = 0
        #se houver alguma linha de inimigos na matriz de inimigos vazia, excluo ela
        for i in matriz_de_inimigos:
            if i == []:
                del matriz_de_inimigos[matriz_de_inimigos.index(i)]

        tiro_delay_player += janela.delta_time()
        tiro_delay_enemy += janela.delta_time()
        move_delay += janela.delta_time()
        Anim_Acc += janela.delta_time()
        if tempo_invencivel < 2:
            tempo_invencivel += janela.delta_time()

        #movimento os inimigos e seto barreiras para o fim do jogo
        if move_delay > 1:
            for linha in matriz_de_inimigos:
                for _ in linha:
                    _.move_x(_.speed*_.direction*dificulty)
            move_delay = 0
        for j in range(len(matriz_de_inimigos)):
            if matriz_de_inimigos[j][-1].x < 0:
                for linha in matriz_de_inimigos:
                    for _ in linha:
                        _.direction *= -1
                        _.move_x(dificulty*_.speed*_.direction+1)
                        _.y += _.height
            elif matriz_de_inimigos[j][0].x + enemy.width > janela.width:
                for linha in matriz_de_inimigos:
                    for _ in linha:
                        _.direction *= -1
                        _.move_x(dificulty*_.speed*_.direction-1)
                        _.y += _.height
            for _ in matriz_de_inimigos[-1]:
                if _.y >= janela.height - player.height - enemy.height:
                    player.clean_tiros()
                    lista_de_tiros_inimigos.clear()
                    matriz_de_inimigos.clear()
                    del player
                    return pont
                
        #paro a animação do player quando ele fica mais do que 2 segundos invencível
        if tempo_invencivel >= 2:
            player.stop()
            player.set_curr_frame(0)

        #controle manual de animação porque por algum motivo a classe Animation não funciona direito
        if Switch_timer and tempo_invencivel < 2:
            player.set_curr_frame(0)
        elif not Switch_timer and tempo_invencivel <2:
            player.set_curr_frame(1)
        if Anim_Acc > 0.300:
            Anim_Acc = 0.000
            Switch_timer = not Switch_timer

        #background color
        janela.set_background_color(background_color)
        #renderizo todos os inimigos da matriz
        for linha in matriz_de_inimigos:
            for _ in linha:
                _.draw()
        player.draw()
        #renderizo os tiros da lista do player
        player.draw_player_tiros()
        #renderizo os tiros da lista dos inimigos
        enemy.draw_enemy_tiros()


        janela.draw_text(f"{len(player.lista_de_tiros_player)}", 0, 20, size=20, color=(255,255,255), font_name="Arial", bold=True, italic=False)
        fps = clock.get_fps()
        janela.draw_text(f"{int(fps)}", 0, 0, size=20, color=(255,255,255), font_name="Arial", bold=True, italic=False)
        janela.draw_text(f"{len(lista_de_tiros_inimigos)}", 0, 40, size=20, color=(255,255,255), font_name="Arial", bold=True, italic=False)
        janela.draw_text(f"{player.vidas}", janela.width-20, 0, size=20, color=(255,255,255), font_name="Arial", bold=True, italic=False)
        clock.tick()
        player.update()
        janela.update()
        if teclado.key_pressed("esc"):
            player.clean_tiros()
            lista_de_tiros_inimigos.clear()
            matriz_de_inimigos.clear()
            del player
            return -1
        

def menu_dificulty():
    botao_facil.set_position(botao_menu_x,150)
    botao_medio.set_position(botao_menu_x,400)
    botao_dificil.set_position(botao_menu_x,650)

    dif = 2
    col = 10
    lin = 5

    while True:
        if mouse.is_over_object(botao_facil) and mouse.is_button_pressed(1):
            dif = 1
            col = 7
            lin = 3
            break

        elif mouse.is_over_object(botao_medio) and mouse.is_button_pressed(1):
            dif = 2
            col = 10
            lin = 5
            break

        elif mouse.is_over_object(botao_dificil) and mouse.is_button_pressed(1):
            dif = 3
            col = 12
            lin = 6
            break

        elif teclado.key_pressed("esc"):
            break

        fps = clock.get_fps()
        
        janela.set_background_color(background_color)
        botao_facil.draw()
        botao_medio.draw()
        botao_dificil.draw()
        janela.draw_text("Fácil", botao_menu_x+45, 190, size=20, color=(255,255,255), font_name="Arial", bold=True, italic=False)
        janela.draw_text("Médio", botao_menu_x+40, 440, size=20, color=(255,255,255), font_name="Arial", bold=True, italic=False)
        janela.draw_text("Difícil", botao_menu_x+44, 690, size=20, color=(255,255,255), font_name="Arial", bold=True, italic=False)

        janela.draw_text(f"{int(fps)}", 0, 0, size=20, color=(255,255,255), font_name="Arial", bold=True, italic=False)
        clock.tick()
        janela.update()
    return dif,col,lin

def show_ranking():

    matriz_ranking = []
    with open("ranking.txt") as f:
        for line in f:
            matriz_ranking.append(line.strip())
    
    matriz_ranking.sort(key=aux_funtion_sorted, reverse=True)
    with open("ranking.txt","w") as f:
        for line in matriz_ranking:
            f.write(f"{line}\n")
    matriz_ranking = matriz_ranking[:5]

    while True:
        
        if teclado.key_pressed("esc"):
            return

        fps = clock.get_fps()


        janela.set_background_color(background_color)
        for i in range(len(matriz_ranking)):
            janela.draw_text(f"{i+1}° {matriz_ranking[i]}", 20, 40*(i+1), size=20, color=(255,255,255), font_name="Arial", bold=True, italic=False)
        janela.draw_text(f"{int(fps)}", 0, 0, size=20, color=(255,255,255), font_name="Arial", bold=True, italic=False)
        clock.tick()
        janela.update()
    
        

while True:
    remember_Col = Col
    remember_Lin = Lin
    if mouse.is_over_object(botao_jogar) and mouse.is_button_pressed(1):
        pontuacao_atual = gameloop()
        if pontuacao_atual != -1:
            nome = input("digite seu nome para a pontuação: ")
            data_atual = str(datetime.now())[:19]
            with open("ranking.txt", "a") as f:
                f.write(f"{nome} - {pontuacao_atual} - {data_atual}\n")
        janela.delay(300)
        Col = remember_Col
        Lin = remember_Lin

    elif mouse.is_over_object(botao_dif) and mouse.is_button_pressed(1):
        dificulty,Col,Lin = menu_dificulty()[0],menu_dificulty()[1],menu_dificulty()[2]
        janela.delay(300)

    elif mouse.is_over_object(botao_ranking) and mouse.is_button_pressed(1):
        show_ranking()
        janela.delay(300)
    
    elif mouse.is_over_object(botao_sair) and mouse.is_button_pressed(1):
        break
    
    janela.set_background_color(background_color)
    botao_jogar.draw()
    botao_dif.draw()
    botao_ranking.draw()
    botao_sair.draw()

    janela.draw_text("Jogar", botao_menu_x+40, 140, size=20, color=(255,255,255), font_name="Arial", bold=True, italic=False)
    janela.draw_text("Dificuldade", botao_menu_x+20, 340, size=20, color=(255,255,255), font_name="Arial", bold=True, italic=False)
    janela.draw_text("Ranking", botao_menu_x+30, 540, size=20, color=(255,255,255), font_name="Arial", bold=True, italic=False)
    janela.draw_text("Sair", botao_menu_x+50, 740, size=20, color=(255,255,255), font_name="Arial", bold=True, italic=False)
    janela.draw_text(f"{dificulty}", 0, 20, size=20, color=(255,255,255), font_name="Arial", bold=True, italic=False)
    
 
    fps = clock.get_fps()
    janela.draw_text(f"{int(fps)}", 0, 0, size=20, color=(255,255,255), font_name="Arial", bold=True, italic=False)
    clock.tick()
    janela.update()
    




"""
To-do-List


"""


