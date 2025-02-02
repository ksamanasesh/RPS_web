from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse
import random
from .models import game_db
from django.db.models import Count, F, Case , When, IntegerField

# Create your views here.
def test(request):
    test = '<h1>Rock Paper Scissors</h1>'
    return(HttpResponse(test))

def home(request):
    return render(request, 'home.html')

def play(request):
    if request.method == 'POST':
        user_name = request.POST.get('user_name')
        request.session['user_name'] = user_name
        request.session['user_score'] = 0
        request.session['bot_score'] = 0
        return redirect('game')

    return render(request, 'play.html')

def game(request):
    user_name = request.session.get('user_name')
    user_score = request.session.get('user_score', 0)
    bot_score = request.session.get('bot_score', 0)

    if request.method == 'POST':
        user_choice = int(request.POST.get('choice'))
        bot_choice = random.randint(0, 2)
        result = determine_winner(user_choice, bot_choice)

        if result == 'win':
            user_score += 1
        elif result == 'lose':
            bot_score += 1

        request.session['user_score'] = user_score
        request.session['bot_score'] = bot_score

        # Check if the game has ended
        if user_score == 10 or bot_score == 10:
            # Save the game result to the database
            game_db.objects.create(
                user_name=user_name,
                user_score=user_score,
                bot_score=bot_score
            )
            # Redirect to the result page
            return JsonResponse({
                'game_over': True,
                'redirect_url': 'result'
            })

        return JsonResponse({
            'user_score': user_score,
            'bot_score': bot_score,
            'result': result,
            'bot_choice': bot_choice,
            'game_over': False
        })

    return render(request, 'game.html', {
        'user_name': user_name,
        'user_score': user_score,
        'bot_score': bot_score
    })

def result(request):
    user_name = request.session.get('user_name')
    user_score = request.session.get('user_score', 0)
    bot_score = request.session.get('bot_score', 0)

    if user_score > bot_score:
        result_text = "Congratulations, You Won the Game!"
    else:
        result_text = "Better luck next time... Smith Won the Game."

    # Clear the session data for a new game
    request.session['user_score'] = 0
    request.session['bot_score'] = 0

    # Get the top 3 users with the highest wins
    top_users = game_db.objects.values('user_name').annotate(
    total_wins=Count(
        Case(
            When(user_score__gt=F('bot_score'), then=1),
            output_field=IntegerField()
        )
    )
    ).order_by('-total_wins')[:3]

    return render(request, 'result.html', {
        'result_text': result_text,
        'top_users': top_users
    })

def leaderboard(request):
    # Get the top 10 users with the highest wins
    top_users = game_db.objects.values('user_name').annotate(
    total_wins=Count(
        Case(
            When(user_score__gt=F('bot_score'), then=1),
            output_field=IntegerField()
        )
    )
    ).order_by('-total_wins')[:3]

    return render(request, 'leaderboard.html', {
        'top_users': top_users
    })

def determine_winner(user_choice, bot_choice):
    if user_choice == bot_choice:
        return 'tie'
    elif (user_choice == 0 and bot_choice == 2) or \
         (user_choice == 1 and bot_choice == 0) or \
         (user_choice == 2 and bot_choice == 1):
        return 'win'
    else:
        return 'lose'