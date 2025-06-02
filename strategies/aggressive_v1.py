# aggressive.py - AI-Enhanced High Risk Mode (Tightened to 18% DD)
import random
import math
from datetime import datetime

class AggressiveBot:
    def __init__(self, capital, mode="aggressive", **kwargs):
        self.capital = capital
        self.initial_capital = capital
        self.leverage = kwargs.get('leverage', 3)  # Reduced leverage for tighter control
        self.mode = mode
        self.dd_limit = kwargs.get('max_drawdown', 0.18)  # Tightened to 18% max drawdown
        self.max_position_size = kwargs.get('max_position', 0.15)  # Reduced to 15% per trade
        self.risk_multiplier = kwargs.get('risk_multiplier', 1.5)  # Reduced risk multiplier
        
        # Aggressive trading parameters (tightened)
        self.target_return = kwargs.get('target_return', 0.06)  # Reduced to 6% daily target
        self.stop_loss = kwargs.get('stop_loss', 0.02)  # Tighter 2% stop loss
        self.take_profit = kwargs.get('take_profit', 0.10)  # Reduced take profit
        self.max_daily_trades = kwargs.get('max_daily_trades', 15)  # Reduced trades
        
        # Tighter risk controls
        self.emergency_stop_dd = 0.15  # Emergency stop at 15%
        self.size_reduction_dd = 0.12  # Start reducing size at 12%
        
        # AI enhancements
        self.use_leverage_scaling = kwargs.get('leverage_scaling', True)
        self.momentum_trading = kwargs.get('momentum_trading', True)
        self.breakout_focus = kwargs.get('breakout_focus', True)
        
        # Performance tracking
        self.daily_trades = 0
        self.consecutive_wins = 0
        self.consecutive_losses = 0
        self.max_consecutive_wins = 0
        self.trade_history = []
        self.peak_capital = capital
        self.daily_pnl = 0
        self.hot_streak_multiplier = 1.0
        
    def signal_ok(self, data):
        """Aggressive signal detection - looking for strong momentum and breakouts"""
        momentum = data.get('momentum', 0.5)
        trend_strength = data.get('trend_strength', 0.5)
        breakout_score = data.get('breakout_score', 0.5)
        volatility = data.get('volatility', 0.1)
        volume_spike = data.get('volume_spike', False)
        ai_confidence = data.get('ai_confidence', 0.5)
        regime = data.get('regime', 'unknown')
        
        # Aggressive requirements - we want HIGH momentum and volatility
        momentum_ok = abs(momentum) > 0.6  # Strong directional momentum
        trend_ok = trend_strength > 0.55   # Strong trend
        breakout_ok = breakout_score > 0.7 # Strong breakout signal
        vol_ok = volatility > 0.04         # Sufficient volatility for profits
        confidence_ok = ai_confidence > 0.6 # AI confidence
        
        # Volume confirmation (aggressive traders need liquidity)
        volume_ok = volume_spike or data.get('volume_ratio', 1.0) > 1.3
        
        # Regime preferences for aggressive trading
        regime_ok = True
        if regime in ['high_volatility', 'trending_bull', 'trending_bear']:
            regime_ok = True  # Love volatility and trends
        elif regime == 'sideways':
            # Still trade sideways but with higher requirements
            momentum_ok = abs(momentum) > 0.75
            breakout_ok = breakout_score > 0.8
        elif regime == 'low_volatility':
            # Avoid low volatility unless signals are exceptional
            if volatility < 0.03:
                return False
        
        # Special aggressive filters
        rsi = data.get('rsi', 50)
        rsi_extreme = rsi < 25 or rsi > 75  # Want extreme RSI for aggressive entries
        
        confluence = data.get('confluence', 0.5)
        confluence_ok = confluence > 0.65
        
        return all([momentum_ok, trend_ok, breakout_ok, vol_ok, confidence_ok, 
                   volume_ok, regime_ok, rsi_extreme, confluence_ok])
    
    def calculate_position_size(self, data):
        """Aggressive position sizing with leverage and hot streak bonuses"""
        base_size = self.capital * self.max_position_size
        
        # AI-enhanced sizing
        if 'position_size' in data:
            ai_suggested_size = data['position_size'] * self.capital
            base_size = max(base_size, ai_suggested_size)  # Take larger of the two
        
        # Confidence multiplier
        confidence = data.get('ai_confidence', 0.5)
        confidence_mult = 0.7 + (confidence * 0.6)  # 70%-130% based on confidence
        
        # Momentum multiplier (aggressive loves momentum)
        momentum = abs(data.get('momentum', 0.5))
        momentum_mult = 0.8 + (momentum * 0.4)  # 80%-120% based on momentum
        
        # Hot streak multiplier (increase size during winning streaks)
        if self.consecutive_wins >= 3:
            self.hot_streak_multiplier = 1 + (self.consecutive_wins * 0.1)
            self.hot_streak_multiplier = min(2.0, self.hot_streak_multiplier)  # Max 2x
        else:
            self.hot_streak_multiplier = max(1.0, self.hot_streak_multiplier * 0.95)
        
        # Cold streak protection (reduce size during losing streaks)
        cold_streak_mult = 1.0
        if self.consecutive_losses >= 2:
            cold_streak_mult = max(0.3, 1 - (self.consecutive_losses * 0.15))
        
        # Leverage scaling based on volatility and regime
        leverage_mult = 1.0
        if self.use_leverage_scaling:
            volatility = data.get('volatility', 0.1)
            regime = data.get('regime', 'unknown')
            
            # High volatility = higher leverage potential
            vol_leverage = min(1.5, 1 + (volatility * 2))
            
            # Regime-based leverage
            regime_leverage = {
                'trending_bull': 1.3,
                'trending_bear': 1.2,
                'high_volatility': 1.4,
                'sideways': 0.8,
                'low_volatility': 0.9
            }.get(regime, 1.0)
            
            leverage_mult = vol_leverage * regime_leverage
        
        # Size reduction for approaching drawdown limit
        current_dd = (self.initial_capital - self.capital) / self.initial_capital
        if current_dd > self.size_reduction_dd:
            size_reduction_factor = 0.5  # Cut size in half
        else:
            size_reduction_factor = 1.0
        
        # Apply all multipliers with size reduction
        final_size = (base_size * confidence_mult * momentum_mult * 
                     self.hot_streak_multiplier * cold_streak_mult * leverage_mult * size_reduction_factor)
        
        # Tighter aggressive bounds
        final_size = min(final_size, self.capital * 0.20)  # Max 20% per trade (reduced from 40%)
        final_size = max(final_size, self.capital * 0.02)  # Min 2% per trade
        
        return final_size
    
    def trade(self, data):
        """Execute aggressive trade with full risk management"""
        if self.daily_trades >= self.max_daily_trades:
            return "⏸️ Daily trade limit reached"
        
        # Drawdown check with tighter limits
        current_dd = (self.initial_capital - self.capital) / self.initial_capital
        if current_dd > self.dd_limit:
            return f"🚨 AGGRESSIVE STOP: Drawdown {current_dd:.1%} exceeds {self.dd_limit:.1%}"
        
        # Signal validation
        if not self.signal_ok(data):
            return "🚫 No trade — insufficient aggressive confluence"
        
        # Position sizing
        trade_size = self.calculate_position_size(data)
        
        # Aggressive execution with enhanced probabilities
        confidence = data.get('ai_confidence', 0.5)
        momentum = abs(data.get('momentum', 0.5))
        trend_strength = data.get('trend_strength', 0.5)
        breakout_score = data.get('breakout_score', 0.5)
        regime = data.get('regime', 'unknown')
        
        # Aggressive success probability calculation
        base_success_prob = (confidence + momentum + trend_strength + breakout_score) / 4
        
        # Hot streak bonus
        streak_bonus = min(0.15, self.consecutive_wins * 0.03)
        
        # Regime-specific success rates for aggressive trading
        regime_success_adj = {
            'trending_bull': 1.2,
            'trending_bear': 1.15,
            'high_volatility': 1.1,  # Aggressive thrives in volatility
            'sideways': 0.9,
            'low_volatility': 0.85
        }
        
        final_success_prob = (base_success_prob + streak_bonus) * regime_success_adj.get(regime, 1.0)
        final_success_prob = min(0.80, max(0.25, final_success_prob))
        
        # Execute trade
        if random.random() < final_success_prob:
            # WINNING TRADE - Aggressive profit calculation
            base_profit_pct = random.uniform(0.05, 0.15)  # Higher base profits
            
            # Aggressive bonuses
            confidence_bonus = 1 + ((confidence - 0.5) * 0.6)  # Bigger confidence bonus
            momentum_bonus = 1 + (momentum * 0.4)             # Momentum bonus
            hot_streak_bonus = 1 + (self.consecutive_wins * 0.05)  # Streak bonus
            
            # Regime profit multipliers (aggressive gets bigger moves)
            regime_profit_mult = {
                'trending_bull': 1.5,
                'trending_bear': 1.3,
                'high_volatility': 1.6,  # Biggest profits in volatility
                'sideways': 1.0,
                'low_volatility': 0.9
            }.get(regime, 1.0)
            
            final_profit_pct = (base_profit_pct * confidence_bonus * momentum_bonus * 
                               hot_streak_bonus * regime_profit_mult)
            final_profit_pct = min(0.18, final_profit_pct)  # Reduced cap to 18%
            
            profit = trade_size * final_profit_pct
            self.capital += profit
            self.daily_pnl += profit
            
            # Update streaks
            self.consecutive_wins += 1
            self.consecutive_losses = 0
            self.max_consecutive_wins = max(self.max_consecutive_wins, self.consecutive_wins)
            
            # Update peak
            if self.capital > self.peak_capital:
                self.peak_capital = self.capital
            
            self.daily_trades += 1
            
            # Log trade
            trade_record = {
                'timestamp': datetime.utcnow().isoformat(),
                'type': 'WIN',
                'size': trade_size,
                'profit': profit,
                'profit_pct': final_profit_pct,
                'confidence': confidence,
                'regime': regime,
                'streak': self.consecutive_wins,
                'hot_streak_mult': self.hot_streak_multiplier
            }
            self.trade_history.append(trade_record)
            
            return f"🔥 AGGRESSIVE WIN | +${profit:.2f} ({final_profit_pct:.1%}) | Capital: ${self.capital:.2f} | Streak: {self.consecutive_wins}W | Hot: {self.hot_streak_multiplier:.1f}x"
            
        else:
            # LOSING TRADE - Aggressive stop loss
            base_loss_pct = self.stop_loss
            
            # Regime-adjusted stop loss
            regime_loss_adj = {
                'trending_bull': 0.8,   # Tighter stops in trends
                'trending_bear': 0.9,
                'high_volatility': 1.4, # Wider stops in volatility
                'sideways': 1.2,
                'low_volatility': 0.7
            }.get(regime, 1.0)
            
            adjusted_loss_pct = base_loss_pct * regime_loss_adj
            adjusted_loss_pct = min(0.06, adjusted_loss_pct)  # Cap at 6%
            
            loss = trade_size * adjusted_loss_pct
            self.capital -= loss
            self.daily_pnl -= loss
            
            # Update streaks
            self.consecutive_losses += 1
            self.consecutive_wins = 0
            self.hot_streak_multiplier = max(1.0, self.hot_streak_multiplier * 0.9)
            
            self.daily_trades += 1
            
            # Log trade
            trade_record = {
                'timestamp': datetime.utcnow().isoformat(),
                'type': 'LOSS',
                'size': trade_size,
                'loss': loss,
                'loss_pct': adjusted_loss_pct,
                'confidence': confidence,
                'regime': regime,
                'streak': self.consecutive_losses
            }
            self.trade_history.append(trade_record)
            
            return f"❌ AGGRESSIVE LOSS | -${loss:.2f} ({adjusted_loss_pct:.1%}) | Capital: ${self.capital:.2f} | Streak: {self.consecutive_losses}L | Regime: {regime}"
    
    def reset_daily_stats(self):
        """Reset daily counters"""
        self.daily_trades = 0
        self.daily_pnl = 0
    
    def get_status(self):
        """Comprehensive aggressive strategy status"""
        current_dd = (self.initial_capital - self.capital) / self.initial_capital if self.initial_capital > 0 else 0
        total_return = (self.capital - self.initial_capital) / self.initial_capital if self.initial_capital > 0 else 0
        daily_return = self.daily_pnl / self.capital if self.capital > 0 else 0
        
        # Calculate win rate
        recent_trades = self.trade_history[-25:] if len(self.trade_history) >= 25 else self.trade_history
        wins = len([t for t in recent_trades if t['type'] == 'WIN'])
        win_rate = wins / len(recent_trades) if recent_trades else 0
        
        # Calculate average profit per trade
        winning_trades = [t for t in recent_trades if t['type'] == 'WIN']
        avg_win = sum(t['profit'] for t in winning_trades) / len(winning_trades) if winning_trades else 0
        
        losing_trades = [t for t in recent_trades if t['type'] == 'LOSS']
        avg_loss = sum(t['loss'] for t in losing_trades) / len(losing_trades) if losing_trades else 0
        
        return {
            "strategy": "AggressiveBot",
            "capital": self.capital,
            "initial_capital": self.initial_capital,
            "total_return": f"{total_return:.1%}",
            "daily_return": f"{daily_return:.1%}",
            "daily_target": f"{self.target_return:.1%}",
            "drawdown": f"{current_dd:.1%}",
            "consecutive_wins": self.consecutive_wins,
            "consecutive_losses": self.consecutive_losses,
            "max_win_streak": self.max_consecutive_wins,
            "hot_streak_multiplier": f"{self.hot_streak_multiplier:.1f}x",
            "daily_trades": self.daily_trades,
            "total_trades": len(self.trade_history),
            "win_rate": f"{win_rate:.1%}",
            "avg_win": f"${avg_win:.2f}",
            "avg_loss": f"${avg_loss:.2f}",
            "peak_capital": self.peak_capital,
            "leverage": self.leverage,
            "risk_level": "AGGRESSIVE",
            "ai_enhanced": True,
            "timestamp": datetime.utcnow().isoformat()
        }
