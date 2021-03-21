# Program by Wyatt Howe U1762239
# University of Huddersfield

import cv2
import cv2.aruco as aruco
import pygame
import random
import os
import sys
import numpy as np


# Displays a selected background on the given screen
# SCREEN - Pygame screen
# selected_background - int
def display_background(SCREEN, selected_background):
    # Checks to see if the given int is between 1 - 4
    # If so, select that background and return
    # else display default background

    if selected_background == int(1):
        SCREEN.blit(pygame.image.load("Data/background.jpg"), (0, 0))
        return

    if selected_background == int(2):
        SCREEN.blit(pygame.image.load("Data/background2.jpg"), (0, 0))
        return

    if selected_background == int(3):
        SCREEN.blit(pygame.image.load("Data/background3.jpg"), (0, 0))
        return

    if selected_background == int(4):
        SCREEN.blit(pygame.image.load("Data/background4.jpg"), (0, 0))
        return

    SCREEN.blit(pygame.image.load("Data/background.jpg"), (0, 0))


# Displays player on given SCREEN based on the x/y values and given sprite
# x, y - int
# SCREEN - pygame display
# player - Sprite
def display_player(x, y, SCREEN, player):
    SCREEN.blit(player, (x, y))


# Displays an obstacle on screen given the parameters
# obstacle_x, obstacle_height, obstacle_width - int
# obstacle_colour - Colour in RGB format
# SCREEN - pygame display
def display_obstacle(obstacle_x, obstacle_height, obstacle_width, obstacle_colour, SCREEN):
    # Draws two rectangles with a game between them
    top_rect = pygame.draw.rect(SCREEN, obstacle_colour, (obstacle_x, 0, obstacle_width, obstacle_height))
    bottom_obstacle_height = 700 - obstacle_height
    bottom_rect = pygame.draw.rect(SCREEN, obstacle_colour, (obstacle_x, 200 + obstacle_height, obstacle_width,
                                                             bottom_obstacle_height))
    return top_rect, bottom_rect  # returns the two rectangles back


# play_game is where the main game loop occurs
# it displays the player, obstacles and background based on their own functions
# it will then update the players location based on the facial detection
# based on players location it will look to see if it is colliding with any obstacles
# if collision happens it sends you to the game over screen with collected score
# will keep track of score in game
# SCREEN - pygame display
# clock - pygame clock for keeping fps
# selected_background - int
def play_game(SCREEN, clock, selected_background):
    # Obstacle Declarations
    obstacle_x = 500
    obstacle_height = random.randint(150, 450)
    obstacle_width = 70
    obstacle_colour = (211, 253, 117)

    # CV2 camera and cascade for face tracking,
    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    face_cascade = cv2.CascadeClassifier('Data/haarcascade_frontalface_default.xml')

    #Bird and Game Declarations
    bird_sprite = pygame.image.load("Data/bird1.png")
    bird_x = 50
    bird_y = 300
    bird_rect = pygame.Rect(bird_x, bird_y, bird_sprite.get_width(), bird_sprite.get_width())
    score = 0
    new_width = (SCREEN.get_width() * .1)  # just here to catch an error where this isn't set
    running = True
    while running:
        SCREEN.fill((0, 0, 0))
        display_background(SCREEN, selected_background)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    cv2.destroyAllWindows()
                    return 0, score

        # Load Data for getting player face
        ret, frame = camera.read()
        # Detect the faces
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)

        # Draw the rectangle around each face
        frame_width = int(camera.get(3))
        frame_height = int(camera.get(4))
        face_found = False
        # this loops over everything that can has been recognized as a face
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)  # shows rectangle over face
            width_modifier = w / frame_width  # this gets how big the width of the rectangle is compared to the screen
            new_width = (SCREEN.get_width() * width_modifier)  # this gives us the size of the rect to draw based on the
            bird_x = (((frame_width - x) / frame_width) * SCREEN.get_width()) - new_width  # working out where the player should be drawn on the x axis
            bird_y = 700 -(((frame_height - y) / frame_height) * SCREEN.get_height())  # working out where the player should be drawn on the y axis
            #pygame.draw.rect(SCREEN, (0, 0, 0), (bird_x, bird_y, 50, 50))
            display_player(x=bird_x, y=bird_y, SCREEN=SCREEN, player=bird_sprite)  # draw player on specified position
            bird_rect = pygame.Rect(bird_x, bird_y, bird_sprite.get_width(), bird_sprite.get_width())  # rect for collisions
            face_found = True

        if not face_found:  # this is here to catch errors if no faces are found
            display_player(x=bird_x, y=bird_y, SCREEN=SCREEN, player=bird_sprite)
        #Display player based on above calculations

        cv2.imshow("TestWindow", frame)  # shows the face being tracked

        # this moves and updates the obstacles, after a certain point the obstacles are moved back to the start
        obstacle_x_change = -4
        if obstacle_x <= -10:
            obstacle_height = random.randint(150, 450)
            obstacle_x = 500
            score += 1
        obstacle_x += obstacle_x_change

        message_display(SCREEN, ("Score is: " + str(score)), (frame_width/2, 100), 40)  # displays score on screen

        top_rect, bottom_rect = display_obstacle(obstacle_x, obstacle_height, obstacle_width, obstacle_colour, SCREEN)  # Creates the rects for the collisions

        # this checks if the players has collided with the obstacles, if so sends them to the game over screen.
        if bird_rect.colliderect(top_rect) or bird_rect.colliderect(bottom_rect):
            #print("CollisionT")
            cv2.destroyAllWindows()
            return 2, int(score)

        pygame.display.update()  # updates the pygame display
        clock.tick(15)  # sets the FPS to 15 (change based on computer performance)

    #return 2, score


# This simply returns what we need to render text on screen
def text_objects(text, font):
    textSurface = font.render(text, True, (255,255,255))
    return textSurface, textSurface.get_rect()


# This renders the text on screen
def message_display(SCREEN, text, rect_center, text_size):
    largeText = pygame.font.Font('freesansbold.ttf', text_size)
    TextSurf, TextRect = text_objects(text, largeText)
    TextRect.center = rect_center
    SCREEN.blit(TextSurf, TextRect)

# This selects a background based on how many fingers you are holding up
# based on https://github.com/iftheqhar/opencv2_python/blob/master/software/firmware/cam.py
def select_background(SCREEN):
    camera = cv2.VideoCapture(0)  # getting a reference to the camera

    # Loop that counts how many fingers, then breaks out and returns after hitting space
    while (camera.isOpened()):
        ret, frame = camera.read()  # get the image from the camera
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # convert the image to gray
        blur = cv2.GaussianBlur(gray, (5, 5), 0)  # now blur the image
        ret, thresh1 = cv2.threshold(blur, 70, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)  # turn the image to black and white
        cv2.imshow("thresh", thresh1)  # show the image in a window
        contours, hierarchy = cv2.findContours(thresh1, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)  # find contours in the image
        drawing = np.zeros(frame.shape, np.uint8)  # create new array of zeros

        max_area = 0

        # this loops over all contours found
        # it then finds the largest contour
        # this will cover the hand you are holding up
        for i in range(len(contours)):
            cnt = contours[i]
            area = cv2.contourArea(cnt)
            if (area > max_area):
                max_area = area
                ci = i


        cnt = contours[ci]
        hull = cv2.convexHull(cnt)
        moments = cv2.moments(cnt)
        if moments['m00'] != 0:
            cx = int(moments['m10'] / moments['m00'])  # cx = M10/M00
            cy = int(moments['m01'] / moments['m00'])  # cy = M01/M00

        centr = (cx, cy)
        cv2.circle(frame, centr, 5, [0, 0, 255], 2)
        cv2.drawContours(drawing, [cnt], 0, (0, 255, 0), 2)
        cv2.drawContours(drawing, [hull], 0, (0, 0, 255), 2)

        # We then try and find the defects in the contour
        # how many defects we find is how many fingers we are holding up
        cnt = cv2.approxPolyDP(cnt, 0.01 * cv2.arcLength(cnt, True), True)
        hull = cv2.convexHull(cnt, returnPoints=False)
        try:
            if 1:
                defects = cv2.convexityDefects(cnt, hull)
                mind = 0
                maxd = 0
                for i in range(defects.shape[0]):
                    s, e, f, d = defects[i, 0]
                    start = tuple(cnt[s][0])
                    end = tuple(cnt[e][0])
                    far = tuple(cnt[f][0])
                    dist = cv2.pointPolygonTest(cnt, centr, True)
                    cv2.line(frame, start, end, [0, 255, 0], 2)

                    cv2.circle(frame, far, 5, [0, 0, 255], -1)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            cv2.destroyAllWindows()
                            running = False
                            return 0, i
                display_background(SCREEN, i)
                i = 0


            # Now we show the windows so we can see what we are doing
            cv2.imshow('output', drawing)
            cv2.imshow('input', frame)
        except AttributeError:  # catches the error incase it cant find anything
            message_display(SCREEN, "Cant Find Hand", SCREEN.get_rect().center, 40)

        pygame.display.update()  # now update the pygame display



        k = cv2.waitKey(10)
        if k == 27:
            break

# Changes the volume based on the rotation of a aruco marker
def volume_changer(camera):
    ret, frame = camera.read()  #Gets the image from the camera and stores it in frame
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # converts image to gray
    aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)  # get the dictionary of markers
    parameters = aruco.DetectorParameters_create()  # creates parameters for the aruco detector
    corners, ids, rejected_img_points = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)  # returns the corners and ids of found aruco markers
    gray = aruco.drawDetectedMarkers(gray, corners)  # draws the markers onto the image
    cv2.imshow('frame', gray)  # shows the window
    if cv2.waitKey(1) & 0xFF == ord('q'):  # quit out of window by pressing "q"
        cv2.destroyAllWindows()

    # Now we loop through all found markers
    # if we find one with the id 22
    # find if the top left corner is higher than bottom right
    # based on this turn volume up or down
    cnt = -1
    try:
        for i in ids:
            cnt += 1
            if i == 22:
                top_left, bottom_right = int(corners[cnt][0][0][1]), int(corners[cnt][0][3][1])
                if top_left < bottom_right:
                    return int(1)
                elif top_left > bottom_right:
                    return  int(-1)
    except TypeError:
        x = 1

    return 0



def main_menu(SCREEN, selected_background):
    running = True

    #Create varibles for the buttons
    BUTTON_WIDTH = 240
    BUTTON_HEIGHT = 100
    SCREEN_WIDTH_MIDPOINT = SCREEN.get_width()/2
    SCREEN_HEIGHT_MIDPOINT = SCREEN.get_height()/2
    button_colour = (66, 224, 245)
    highlighted_button_colour = (66, 188, 245)

    # clock to keep the fps and track it
    clock = pygame.time.Clock()

    # varibles to create buttons
    play_button_rect = pygame.Rect(SCREEN_WIDTH_MIDPOINT - (BUTTON_WIDTH/2), SCREEN_HEIGHT_MIDPOINT - 200, BUTTON_WIDTH, BUTTON_HEIGHT)
    background_button_rect = pygame.Rect(SCREEN_WIDTH_MIDPOINT - (BUTTON_WIDTH/2), SCREEN_HEIGHT_MIDPOINT - 75, BUTTON_WIDTH, BUTTON_HEIGHT)
    quit_button_rect = pygame.Rect(SCREEN_WIDTH_MIDPOINT - (BUTTON_WIDTH/2), SCREEN_HEIGHT_MIDPOINT + 50, BUTTON_WIDTH, BUTTON_HEIGHT)
    SCREEN.fill((255, 255, 255))

    # holding varible for volume
    volume = 100

    # camera for detecting aruco markers
    camera = cv2.VideoCapture(0)
    while running:

        # display backgrounds and buttons on screen
        display_background(SCREEN, selected_background)
        pygame.draw.rect(SCREEN, button_colour, play_button_rect)
        message_display(SCREEN, "Play", play_button_rect.center, 40)
        pygame.draw.rect(SCREEN, button_colour, quit_button_rect)
        message_display(SCREEN, "Quit", quit_button_rect.center, 40)
        pygame.draw.rect(SCREEN, button_colour, background_button_rect)
        message_display(SCREEN, "Background", background_button_rect.center, 40)

        # Get mouse position
        # Check to see if inside any buttons
        # if it is inside of any buttons
        # if it is, highlight said button
        mouse_pos = pygame.mouse.get_pos()
        if play_button_rect.collidepoint(mouse_pos[0],mouse_pos[1]):
            pygame.draw.rect(SCREEN, highlighted_button_colour, play_button_rect)
            message_display(SCREEN, "Play", play_button_rect.center,40)

        if background_button_rect.collidepoint(mouse_pos[0],mouse_pos[1]):
            pygame.draw.rect(SCREEN, highlighted_button_colour, background_button_rect)
            message_display(SCREEN, "Background", background_button_rect.center,40)

        if quit_button_rect.collidepoint(mouse_pos[0],mouse_pos[1]):
            pygame.draw.rect(SCREEN, highlighted_button_colour, quit_button_rect)
            message_display(SCREEN, "Quit", quit_button_rect.center,40)

        # for any event that happens in pygame
        # see if a button was clicked
        # if so carry out corresponding action
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button_rect.collidepoint(mouse_pos[0], mouse_pos[1]):
                    running = False
                    cv2.destroyAllWindows()
                    return 1
                if background_button_rect.collidepoint(mouse_pos[0], mouse_pos[1]):
                    running = False
                    cv2.destroyAllWindows()
                    return 3
                if quit_button_rect.collidepoint(mouse_pos[0], mouse_pos[1]):
                    running = False
                    pygame.quit()
                    cv2.destroyAllWindows()
        clock.tick(60)

        # adjusts volume based on aruco code
        volume += volume_changer(camera)
        if volume < 0:
            volume = 0
        if volume > 100:
            volume = 100

        # Draw a rectangle on screen to represent volume
        volume_meter = pygame.Rect(0, 10, volume, 10)
        pygame.draw.rect(SCREEN, (0,0,0), volume_meter)

        pygame.display.update() # Update pygame display

    return int(1)


def game_over(SCREEN, score, high_score, selected_background):

    #Varibles to position, size and colour buttons on screen
    BUTTON_WIDTH = 240
    BUTTON_HEIGHT = 100
    SCREEN_WIDTH_MIDPOINT = SCREEN.get_width()/2
    SCREEN_HEIGHT_MIDPOINT = SCREEN.get_height()/2
    button_colour = (66, 224, 245)
    highlighted_button_colour = (66, 188, 245)

    clock = pygame.time.Clock()  # Allows us to set frame rate
    running = True  # Boolean for a while loop
    while running:
        # Creating size of buttons
        play_button_rect = pygame.Rect(SCREEN_WIDTH_MIDPOINT - (BUTTON_WIDTH/2), SCREEN_HEIGHT_MIDPOINT - 200, BUTTON_WIDTH, BUTTON_HEIGHT)
        quit_button_rect = pygame.Rect(SCREEN_WIDTH_MIDPOINT - (BUTTON_WIDTH/2), SCREEN_HEIGHT_MIDPOINT + 50, BUTTON_WIDTH, BUTTON_HEIGHT)

        # Displaying background first so it can be written over.
        display_background(SCREEN, selected_background)

        # Drawing buttons and text on screen
        pygame.draw.rect(SCREEN, button_colour, play_button_rect)
        message_display(SCREEN, "Play", play_button_rect.center, 40)
        pygame.draw.rect(SCREEN, button_colour, quit_button_rect)
        message_display(SCREEN, "Quit", quit_button_rect.center, 40)
        message_display(SCREEN, ("Highscore: " + str(high_score)), (70, 10), 20)
        message_display(SCREEN, ("      Score : " + str(score)), (70, 40), 20)

        mouse_pos = pygame.mouse.get_pos()  # Getting mouse position

        # Checking mouse position against buttons to highlight buttons
        if play_button_rect.collidepoint(mouse_pos[0],mouse_pos[1]):
            pygame.draw.rect(SCREEN, highlighted_button_colour, play_button_rect)
            message_display(SCREEN, "Play", play_button_rect.center,40)
        if quit_button_rect.collidepoint(mouse_pos[0],mouse_pos[1]):
            pygame.draw.rect(SCREEN, highlighted_button_colour, quit_button_rect)
            message_display(SCREEN, "Quit", quit_button_rect.center,40)

        # Checking to see if a button is clicked or pygame is exited
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button_rect.collidepoint(mouse_pos[0], mouse_pos[1]):
                    running = False
                    cv2.destroyAllWindows()
                    return int(1)
                if quit_button_rect.collidepoint(mouse_pos[0], mouse_pos[1]):
                    running = False
                    pygame.quit()
                    cv2.destroyAllWindows()

        pygame.display.update()  # Updating the window to display the changes
    return int(1)


def __main__():
    pygame.init()  # initialize pygame
    pygame.display.set_caption("Move head avoid blocks")  # set title for pygame window

    clock = pygame.time.Clock()  # get clock for FPS

    # set size of pygame window
    size = width, height = 500, 750
    SCREEN = pygame.display.set_mode(size)
    running = True

    # Get highscore, if no save data create the fire
    if not os.path.exists("Data/savedata.txt"):
        save_data = open("Data/savedata.txt", "w+")
        data = "0"
        save_data.writelines(data)
    else:
        save_data = open("Data/savedata.txt", "r")

    # set score and high score
    score = 0
    high_score = save_data.read()

    # set all available scenes and set the current scene to the main menu
    available_scenes = {
        0: "Main_Menu",
        1: "Main_Game",
        2: "Game_Over",
        3: "Background_Select"}
    current_scene = available_scenes.get(0)

    selected_background = 1  # set background to default background

    # loop through the current scene and switch when it returns
    while running:
        # this switches the scenes
        if current_scene == available_scenes.get(0):
            current_scene = available_scenes.get(main_menu(SCREEN, selected_background))
        elif current_scene == available_scenes.get(1):
            next_scene, score = play_game(SCREEN, clock, selected_background)
            # if the score is greater than the high score
            # write over the old save data
            if int(score) > int(high_score):
                string_list = save_data.readlines()
                save_data.close()
                #string_list[0] = str(score)
                write_file = open("Data/savedata.txt", "w")
                write_file.write(str(score))
                write_file.close()
                save_data = open("Data/savedata.txt", "r")
                high_score = save_data.read()
                print(high_score)

            #implement high score here
            current_scene = available_scenes.get(next_scene)
        elif current_scene == available_scenes.get(2):
            current_scene = available_scenes.get(game_over(SCREEN, score, int(high_score), selected_background))
        elif current_scene == available_scenes.get(3):
            next_scene, selected_background = select_background(SCREEN)
            current_scene = available_scenes.get(next_scene)




__main__()

# pygame.quit()
#cv2.destroyAllWindows()


#To Do
#Put game Logic in own function - Done
#Add Menu System - Add some polish
#Finger Detection to change background - Only works in dim lighting
#Marker Detection to change volume - works
#marker detection in own scene - fixed to be part of main menu
#Implement high score - done
#comment code