import pygame
from pygame.locals import *
import random
import sys

# Initialisation de Pygame
pygame.init()

# Définition du clock et FPS (Frames per second)
clock = pygame.time.Clock()  # Crée un objet Clock pour contrôler la vitesse du jeu
fps = 60  # Définition du nombre d'images par seconde

# Taille de la fenêtre
SCREEN_WIDTH = 600  # Largeur de la fenêtre de jeu
SCREEN_HEIGHT = 800  # Hauteur de la fenêtre de jeu
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))  # Crée la fenêtre du jeu
pygame.display.set_caption("Mini-Jeu")  

# Charger le fond
try:
    bg = pygame.image.load("bgg.jpg")  
except pygame.error as e: 
    print(f"Erreur de chargement de l'image : {e}")  
    bg = None  

def draw_bg():
    """Affiche le fond ou un fond noir si l'image échoue."""
    if bg:  # Si l'image du fond est chargée
        screen.blit(bg, (0, 0))  # Dessiner l'image du fond à la position (0, 0)
    else:
        screen.fill((0, 0, 0))  # Sinon, remplir l'écran en noir


score = 0  # Le score initial 
font = pygame.font.SysFont("Arial", 30)  # Définir une police de caractères pour le score

def draw_score():
    """Affiche le score à l'écran."""
    text = font.render(f"Score: {score}", True, (255, 255, 255))  # Créer une surface pour afficher le score
    screen.blit(text, (10, 10))  # Afficher le texte du score à la position (10, 10)

# Classe du vaisseau
class Spaceship(pygame.sprite.Sprite): 
    def __init__(self, x, y):
        super().__init__()  # Appel du constructeur de la classe parente (Sprite)
        self.image = pygame.image.load("spaceship.jpg")  # Charger l'image du vaisseau
        self.image = pygame.transform.scale(self.image, (50, 50))  # Redimensionner l'image du vaisseau
        self.rect = self.image.get_rect()  # Créer un rectangle pour définir la position et les dimensions du vaisseau
        self.rect.center = [x, y]  # Placer le vaisseau à la position (x, y)
        self.health_start = 100  # Vie maximale du vaisseau
        self.health_remaining = 100  # Vie restante du vaisseau
        self.last_shot = pygame.time.get_ticks()  # Temps du dernier tir (en millisecondes)

    def update(self):
        """Déplacement gauche/droite et tir si la santé > 0"""
        if self.health_remaining > 0:  # Si le vaisseau a encore de la vie
            speed = 8  # Vitesse de déplacement
            cooldown = 200  # Temps entre deux tirs
            keys = pygame.key.get_pressed()  # Récupérer l'état des touches du clavier
            if keys[K_LEFT] and self.rect.left > 0:  # Si la touche flèche gauche est pressée et que le vaisseau est à gauche
                self.rect.x -= speed  # Déplacer le vaisseau vers la gauche
            if keys[K_RIGHT] and self.rect.right < SCREEN_WIDTH:  # Si la touche flèche droite est pressée et que le vaisseau est à droite
                self.rect.x += speed  # Déplacer le vaisseau vers la droite
            time_now = pygame.time.get_ticks()  # Obtenir l'heure actuelle en millisecondes
            if keys[K_SPACE] and time_now - self.last_shot > cooldown:  # Si la touche espace est pressée et que le tir est prêt
                bullet = Bullet(self.rect.centerx, self.rect.top)  # Créer une nouvelle balle
                bullets_group.add(bullet)  # Ajouter la balle au groupe de balles
                all_sprites.add(bullet)  # Ajouter la balle au groupe d'objets à dessiner
                self.last_shot = time_now  # Mettre à jour le dernier tir
        else:
            if not self.exploded:  # Si le vaisseau n'a pas encore explosé
                explosion = Explosion(self.rect.centerx, self.rect.centery, 3)  # Créer une explosion à la position du vaisseau
                explosion_group.add(explosion)  # Ajouter l'explosion au groupe d'explosions
                self.exploded = True  # Marquer le vaisseau comme ayant explosé

    def draw_health_bar(self):
        """Affiche la barre de vie du vaisseau."""
        if self.health_remaining > 0:  # Si le vaisseau a de la vie
            pygame.draw.rect(
                screen,
                (0, 255, 0),  # Couleur verte
                (
                    self.rect.x,  # Position x du vaisseau
                    self.rect.bottom + 10,  # Position y juste en dessous du vaisseau
                    int(self.rect.width * (self.health_remaining / self.health_start)),  # Largeur de la barre proportionnelle à la vie
                    15  # Hauteur de la barre
                )
            )

# Classe des balles
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()  # Appel du constructeur de la classe parente (Sprite)
        try:
            self.image = pygame.image.load("bullet.jpg")  # Charger l'image de la balle
            self.image = pygame.transform.scale(self.image, (40, 30))  # Redimensionner l'image de la balle
        except pygame.error:  # Si l'image ne se charge pas
            self.image = pygame.Surface((5, 15))  # Créer une surface de balle par défaut
            self.image.fill((255, 255, 0))  # Remplir la surface avec une couleur jaune
        self.rect = self.image.get_rect()  # Créer un rectangle pour définir la position et les dimensions de la balle
        self.rect.center = [x, y]  # Placer la balle à la position (x, y)

    def update(self):
        global score  # Accéder à la variable score
        self.rect.y -= 5  # Déplacer la balle vers le haut de l'écran
        if self.rect.bottom < 0:  # Si la balle sort de l'écran
            self.kill()  # Supprimer la balle
        if pygame.sprite.spritecollide(self, alien_group, True):  # Si la balle touche un alien
            self.kill()  # Supprimer la balle
            score += 10  # Ajouter 10 au score
            explosion = Explosion(self.rect.centerx, self.rect.centery, 2)  # Créer une explosion à l'impact
            explosion_group.add(explosion)  # Ajouter l'explosion au groupe d'explosions

# Classe des aliens
class Alien(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()  
        idx = random.randint(1, 5)  
        try:
            img = pygame.image.load(f"aliens{idx}.png")  # Charger l'image de l'alien
            self.image = pygame.transform.scale(img, (40, 40))  # Redimensionner l'image de l'alien
        except (pygame.error, FileNotFoundError):  # Si l'image ne se charge pas
            self.image = pygame.Surface((40, 40))  # Créer une surface par défaut pour l'alien
            self.image.fill((0, 255, 0))  # Remplir l'alien avec une couleur verte
        self.rect = self.image.get_rect()  
        self.rect.center = [x, y] 
        self.move_counter = 0  # Compteur pour déplacer l'alien
        self.move_direction = 1  # Direction initiale du mouvement de l'alien (1 = droite)

    def update(self):
        self.rect.x += self.move_direction  # Déplacer l'alien dans la direction actuelle
        self.move_counter += 1  # Incrémenter le compteur
        if abs(self.move_counter) > 75:  # Si le compteur dépasse 75
            self.move_direction *= -1  # Changer la direction du mouvement
            self.move_counter *= self.move_direction  # Réinitialiser le compteur

# Classe d'explosion
class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, size):
        super().__init__()  
        self.images = []  # Liste 
        for num in range(1, 6):  # Charger 5 images d'explosion
            img = pygame.image.load(f"img/exp{num}.png")
            if size == 1:
                img = pygame.transform.scale(img, (20, 20))  # Taille petite explosion
            elif size == 2:
                img = pygame.transform.scale(img, (40, 40))  # Taille moyenne explosion
            elif size == 3:
                img = pygame.transform.scale(img, (160, 160))  # Taille grande explosion
            self.images.append(img)  
        self.index = 0  # Indice de l'image actuelle de l'explosion
        self.image = self.images[self.index]  
        self.rect = self.image.get_rect()  # Créer un rectangle pour l'explosion
        self.rect.center = [x, y]  
        self.counter = 0  # Compteur pour l'animation de l'explosion

    def update(self):
        explosion_speed = 7  # La vitesse de l'animation 
        self.counter += 1  # Incrémenter le compteur
        if self.counter >= explosion_speed and self.index < len(self.images) - 1:  # Si le compteur est assez élevé et qu'il reste des images à afficher
            self.counter = 0  
            self.index += 1  # Passer l'image suivante
            self.image = self.images[self.index] 
        if self.index >= len(self.images) - 1 and self.counter >= explosion_speed:  # Si toutes les images ont été affichées
            self.kill()  

# Fonction pour créer les aliens
def create_aliens():
    for row in range(3):  
        for col in range(5):  # Créer 5 aliens par rangée
            alien = Alien(100 + col * 100, 100 + row * 70)  
            alien_group.add(alien)  
            all_sprites.add(alien)  

# Bouton rejouer
def draw_restart_button():
    pygame.draw.rect(screen, (255, 255, 255), (200, 500, 200, 60))  # Dessiner un rectangle blanc pour le bouton
    font_btn = pygame.font.SysFont("Arial", 35)  # Définir une police pour le texte du bouton
    text = font_btn.render("REJOUER", True, (0, 0, 0))  # Créer une surface pour le texte "REJOUER"
    screen.blit(text, (220, 510))  # Afficher le texte du bouton au centre du rectangle

# === Boucle principale ===
def main_game():
    global score  
    score = 0 
    run = True  
    game_over = False  
    spaceship_exploded = False  #le vaisseau a explosé
    explosion_done = False  # si l'explosion est terminée

    spaceship = Spaceship(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)  # Créer un vaisseau au bas de l'écran
    spaceship_group.add(spaceship)  # Ajouter le vaisseau au groupe du vaisseau
    all_sprites.add(spaceship)  # Ajouter le vaisseau au groupe de tous les objets à dessiner
    create_aliens() 

    while run:  
        clock.tick(fps)  # Limit  boucle à 60 images par seconde
        for event in pygame.event.get(): 
            if event.type == pygame.QUIT:  
                pygame.quit()  
                sys.exit()  

            if game_over and event.type == pygame.MOUSEBUTTONDOWN:  # Si le jeu est termine
                if pygame.Rect(200, 500, 200, 60).collidepoint(event.pos):  # Si le clic est sur le bouton "REJOUER"
                    spaceship_group.empty()  # Vider les groupes
                    bullets_group.empty()
                    alien_group.empty()
                    all_sprites.empty()
                    explosion_group.empty()
                    main_game()  # Relancer le jeu

        # Mise à jour des groupes
        if not game_over:
            all_sprites.update()  # Mettre à jour tous les objets
            explosion_group.update()  # Mettre à jour les explosions
            pygame.sprite.groupcollide(bullets_group, alien_group, True, True)  # Collision entre les balles et les aliens

        draw_bg()  
        all_sprites.draw(screen)  # Dessiner tous les objets
        explosion_group.draw(screen)  # Dessiner les explosions

        if spaceship.alive():  # Si le vaisseau est encore en vie
            spaceship.draw_health_bar()  # Afficher la barre de vie

        draw_score()  # Afficher le score

        # === FIN DU JEU ===
        if not game_over and len(alien_group) == 0:  # Si tous les aliens sont détruits
            if not spaceship_exploded:
                explosion = Explosion(spaceship.rect.centerx, spaceship.rect.centery, 3)  # Créer une explosion au centre du vaisseau
                explosion_group.add(explosion)  # Ajouter l'explosion au groupe
                spaceship.kill()  # Detruire le vaisseau
                spaceship_exploded = True  # Marquer que le vaisseau a explosé
            if spaceship_exploded and len(explosion_group) == 0 and not explosion_done:
                explosion_done = True  # Marquer que l'explosion est terminée
                game_over = True  # Fin 

        if game_over:  
            font_end = pygame.font.SysFont("Arial", 60)  # Définir une police pour l'écran de fin
            text = font_end.render("GAME OVER", True, (255, 0, 0))  # Créer une surface pour "GAME OVER"
            screen.blit(text, (SCREEN_WIDTH // 2 - 160, SCREEN_HEIGHT // 2 - 30))  # Afficher "GAME OVER" au centre
            draw_restart_button()  

        pygame.display.update()  # Mettre à jour l'affichage

# === Lancer le jeu ===
spaceship_group = pygame.sprite.Group()  # Créer un groupe pour le vaisseau
bullets_group = pygame.sprite.Group()  # Créer un groupe pour les balles
all_sprites = pygame.sprite.Group()  # Créer un groupe pour tous les objets à dessiner
alien_group = pygame.sprite.Group()  # Créer un groupe pour les aliens
explosion_group = pygame.sprite.Group()  # Créer un groupe pour les explosions

main_game() 