# flip_v2.py - AI-Enhanced Full Send Mode for 100% Daily Compounding
import random
import math
from datetime import datetime

class FlipBotV2:
    def __init__(self, capital, risk_mode="full_send", **kwargs):
        self.capital = capital
        self.initial_capital = capital
        self.risk_mode = risk_mode
        self.daily_target = 1.0  # 100% daily target
        self.max_dd = kwargs.get("max_drawdown", 0.20)  # 20% for flip potential
        self.consecutive_losses = 0
        self.daily_trades = 0
        self.max_daily_trades = kwargs.get("max_daily_trades", 15)
        self.max_position_size = 0.35  # 35% per trade for flip power
        self.stop_loss = 0.02
        
        # Performance tracking
        self.trade_history = []
        self.peak_capital = capital
        self.current_streak = 0
        self.best_streak = 0
        
    def check_signal(self, market_data):
        vol = market_data.get("volatility", 0)
        breakout = market_data.get("breakout_score", 0)
        confidence = market_data.get("ai_confidence", 0.5)
        momentum = market_data.get("momentum", 0.5)
        
        # FLIP MODE: Aggressive signal requirements
        vol_ok = 0.03 < vol < 0.25
        breakout_ok = breakout > 0.75
        confidence_ok = confidence > 0.6
        momentum_ok = abs(momentum) > 0.4
        
        return vol_ok and breakout_ok and confidence_ok and momentum_ok
    
    def calculate_position_size(self, market_data):
        confidence = market_data.get("ai_confidence", 0.5)
        
        # Calculate progress toward 100% daily target
        current_return = (self.capital - self.initial_capital) / self.initial_capital
        remaining_target = max(0, self.daily_target - current_return)
        trades_left = max(1, self.max_daily_trades - self.daily_trades)
        
        # Size to hit remaining target
        if remaining_target > 0:
            target_per_trade = remaining_target / trades_left
            base_size = self.capital * min(target_per_trade, self.max_position_size)
        else:
            base_size = self.capital * 0.05  # Reduce after target hit
        
        # Confidence scaling for FLIP mode
        confidence_mult = 0.7 + (confidence * 0.6)  # 70%-130%
        
        # Hot streak bonus
        if self.current_streak > 0:
            streak_mult = 1 + (self.current_streak * 0.1)  # 10% per win
            streak_mult = min(1.5, streak_mult)
        else:
            streak_mult = 1.0
        
        # Cold streak protection
        if self.consecutive_losses >= 2:
            loss_mult = max(0.5, 1 - (self.consecutive_losses * 0.15))
        else:
            loss_mult = 1.0
        
        final_size = base_size * confidence_mult * streak_mult * loss_mult
        
        # FLIP bounds
        final_size = min(final_size, self.capital * self.max_position_size)
        final_size = max(final_size, self.capital * 0.02)
        
        return final_size
    
    def trade(self, market_data):
        if self.daily_trades >= self.max_daily_trades:
            return "⏸️ Daily trade limit reached"
            
        # Check daily target
        current_return = (self.capital - self.initial_capital) / self.initial_capital
        if current_return >= self.daily_target:
            return f"🎯 FLIP TARGET HIT! {current_return:.1%}"
            
        # Drawdown check
        current_dd = (self.initial_capital - self.capital) / self.initial_capital
        if current_dd > self.max_dd:
            return f"🚨 FLIP STOP: DD {current_dd:.1%}"
        
        if not self.check_signal(market_data):
            return "⏸️ No flip signal"
        
        trade_size = self.calculate_position_size(market_data)
        confidence = market_data.get("ai_confidence", 0.5)
        
        # FLIP execution - higher success rate for aggressive moves
        success_prob = 0.55 + (confidence * 0.25)  # 55-80%
        
        if random.random() < success_prob:
            # WIN - Target big moves for compounding
            profit_pct = random.uniform(0.08, 0.25) * (1 + confidence * 0.5)
            profit_pct = min(0.35, profit_pct)  # Cap at 35%
            
            profit = trade_size * profit_pct
            self.capital += profit
            
            self.consecutive_losses = 0
            self.current_streak += 1
            self.best_streak = max(self.best_streak, self.current_streak)
            if self.capital > self.peak_capital:
                self.peak_capital = self.capital
            
            self.daily_trades += 1
            
            # Recalculate progress after updating capital
            new_return = (self.capital - self.initial_capital) / self.initial_capital
            progress = (new_return / self.daily_target) * 100
            return (
                f"🚀 FLIP WIN | +${profit:.2f} ({profit_pct:.1%}) | "
                f"Capital: ${self.capital:.2f} | Progress: {progress:.0f}%"
            )
            
        else:
            # LOSS
            loss_pct = self.stop_loss * random.uniform(0.8, 1.2)
            loss_pct = min(0.04, loss_pct)
            
            loss = trade_size * loss_pct
            self.capital -= loss
            
            self.consecutive_losses += 1
            self.current_streak = 0
            self.daily_trades += 1
            
            # Recalculate remaining progress after loss
            new_return = (self.capital - self.initial_capital) / self.initial_capital
            remaining = max(0, (self.daily_target - new_return) * 100)
            return (
                f"❌ FLIP LOSS | -${loss:.2f} | Capital: ${self.capital:.2f} "
                f"| Need: {remaining:.0f}%"
            )
    
    def get_status(self):
        current_dd = (self.initial_capital - self.capital) / self.initial_capital if self.initial_capital > 0 else 0
        total_return = (self.capital - self.initial_capital) / self.initial_capital if self.initial_capital > 0 else 0
        progress = (total_return / self.daily_target) * 100
        
        return {
            "strategy": "FlipBotV2_COMPOUND_MODE",
            "capital": self.capital,
            "total_return": f"{total_return:.1%}",
            "daily_progress": f"{progress:.0f}%",
            "target": "100% DAILY",
            "drawdown": f"{current_dd:.1%}",
            "streak": self.current_streak,
            "trades": self.daily_trades,
            "flip_mode": "ACTIVE"
        }
