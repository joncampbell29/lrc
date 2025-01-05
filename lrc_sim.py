import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from tqdm import tqdm
from numba import jit

DICE_SIDES = np.array([0, 0, 0, 1, 2, 3], dtype=np.int32)

@jit(nopython=True)
def process_dice_rolls(money, num_dice):
    if money <= 0:
        return 0, 0, 0
    num_rolls = min(money, num_dice)
    rolls = np.random.choice(DICE_SIDES, size=num_rolls)
    counts = np.bincount(rolls, minlength=4)
    return counts[1], counts[2], counts[3]


@jit(nopython=True)
def simulate_single_game(num_people, starting_cash, num_dice):
    """Simulate a single game and return results"""
    money_array = np.full(num_people, starting_cash, dtype=np.int32)
    pot = 0
    num_rolls = 0
    active_players = num_people
    while active_players > 1:
        for i in range(num_people):
            if money_array[i] <= 0:
                continue
                
            left_count, right_count, center_count = process_dice_rolls(money_array[i], num_dice)
            total_loss = left_count + right_count + center_count
            
            if total_loss > 0:
                money_array[i] -= total_loss
                money_array[(i - 1) % num_people] += left_count
                money_array[(i + 1) % num_people] += right_count
                pot += center_count
                num_rolls += 1
            
            active_players = np.sum(money_array > 0)
            if active_players == 1:
                break
                
    winner_idx = np.argmax(money_array > 0)
    earnings_array = np.where(money_array > 0, money_array + pot, -starting_cash)
    
    return earnings_array, winner_idx, num_rolls
    
def simulate_lrc(num_people, starting_cash, num_dice=3, num_sims=100):
    wins = np.zeros(num_people, dtype=np.int32)
    earnings = np.zeros(num_people, dtype=np.int32)
    total_rolls = np.zeros(num_sims, dtype=np.int16)
    
    for sim in tqdm(range(num_sims)):
        earnings_array, winner_idx, num_rolls = simulate_single_game(num_people, starting_cash, num_dice)
        wins[winner_idx] += 1
        earnings += earnings_array
        total_rolls[sim] = num_rolls
    
    avg_rolls = np.mean(total_rolls)
    sd_rolls = np.std(total_rolls)
    
    data = {
        'num_players': num_people,
        'starting_cash': starting_cash,
        'num_dice': num_dice,
        'num_sims': num_sims,
        'avg_rolls': avg_rolls,
        'sd_rolls': sd_rolls,
        'wins': wins,
        'earnings': earnings,
        'win_pct': wins / num_sims,
        'expected_earnings': earnings / num_sims,
        'player_id': list(range(num_people))
    }
    
    return data

