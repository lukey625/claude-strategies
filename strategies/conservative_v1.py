# conservative.py - AI-Enhanced Ultra-Conservative Strategy (3% DD, 1% Daily)
import random
import math
from datetime import datetime

class ConservativeBot:
    def __init__(self, capital, **kwargs):
        self.capital = capital
        self.initial_capital = capital
        self.daily_target = kwargs.get('daily_target', 0.01)  # 1% daily target as requested
        self.risk_cap = kwargs.get('risk_cap', 0.015)  # Reduced to 1.5% max risk per trade
        self.max_drawdown = kwargs.get('max_drawdown', 0.03)  # Tightened to 3% max drawdown
        self.stop_loss = kwargs.get('stop_loss', 0.005)  # Ultra-tight 0.5% stop loss
        
        # Ultra-conservative parameters
        self.max_daily_trades = kwargs.get('max_daily_trades', 4)  # Reduced to 4 trades max
        self.min_confidence = kwargs.get('min_confidence', 0.8)   # Even higher confidence required
        self.min_win_rate_required = kwargs.get('min_win_rate', 0.75)  # 75% win rate target
        self.profit_target = kwargs.get('profit_target', 0.012)  # 1.2% per trade target
        
        # Ultra-tight risk controls
        self.emergency_stop_dd = 0.025  # Emergency stop at 2.5%
        self.size_reduction_dd = 0.02   # Start reducing size at 2%
        
        # Safety mechanisms
        self.safety_first = kwargs.get('safety_first', True)
        self.preserve_capital = kwargs.get('preserve_capital', True)
        self.gradual_scaling = kwargs.get('gradual_scaling', True)
        
        # Performance tracking
        self.daily_trades = 0
        self.daily_profit = 0
        self.trade_history = []
        self.daily_history = []
        self.consecutive_profitable_days = 0
        self.total_profitable_days = 0
        self.peak_capital = capital
        self.safety_violations = 0
        
    def can_trade(self, metrics):
        """Ultra-strict trading conditions"""
        # Basic market health checks
        spread = metrics.get('spread', 0.001)
        volume = metrics.get('volume', 1000000)
        volatility = metrics.get('volatility', 0.1)
        ai_confidence = metrics.get('ai_confidence', 0.5)
        regime = metrics.get('regime', 'unknown')
        
        # Conservative requirements
        spread_ok = spread < 0.002           # Tight spreads only
        volume_ok = volume > 1000000         # High volume only
        vol_ok = 0.01 < volatility < 0.08    # Low to moderate volatility
        confidence_ok = ai_confidence >= self.min_confidence  # High confidence only
        
        # Regime preferences (ultra-conservative)
        regime_ok = regime in ['trending_bull', 'low_volatility', 'sideways']
        if regime == 'high_volatility':
            return False  # Never trade in high volatility
        
        # Additional safety checks
        support_resistance = metrics.get('support_resistance', 0.5)
        trend_strength = metrics.get('trend_strength', 0.5)
        confluence = metrics.get('confluence', 0.5)
        
        sr_ok = support_resistance > 0.7     # Strong S/R levels
        trend_ok = trend_strength > 0.6      # Strong trend
        confluence_ok = confluence > 0.75    # High confluence
        
        # Market timing (avoid risky periods)
        rsi = metrics.get('rsi', 50)
        rsi_ok = 35 < rsi < 65  # Avoid extreme RSI
        
        # Volume profile check
        volume_profile = metrics.get('volume_profile', 1.0)
        volume_profile_ok = volume_profile > 0.8
        
        return all([spread_ok, volume_ok, vol_ok, confidence_ok, regime_ok,
                   sr_ok, trend_ok, confluence_ok, rsi_ok, volume_profile_ok])
    
    def calculate_position_size(self, metrics):
        """Ultra-conservative position sizing"""
        # Start with minimal base size
        base_size = self.capital * 0.01  # 1% base
        
        # AI sizing (but capped conservatively)
        if 'position_size' in metrics:
            ai_size = metrics['position_size'] * self.capital
            # Take smaller of AI suggestion and conservative limit
            base_size = min(base_size, ai_size, self.capital * self.risk_cap)
        
        # Confidence scaling (only increase for very high confidence)
        confidence = metrics.get('ai_confidence', 0.5)
        if confidence > 0.8:
            confidence_mult = 1 + ((confidence - 0.8) * 0.5)  # Max 1.1x for 100% confidence
        else:
            confidence_mult = 0.8  # Reduce size for lower confidence
        
        # Drawdown protection (reduce size as drawdown increases)
        current_dd = (self.initial_capital - self.capital) / self.initial_capital
        dd_protection = max(0.3, 1 - (current_dd * 5))  # Aggressive reduction
        
        # Daily profit protection (reduce size as we approach daily target)
        daily_return = self.daily_profit / self.capital if self.capital > 0 else 0
        if daily_return >= self.daily_target * 0.8:  # 80% of target reached
            daily_mult = 0.5  # Cut size in half
        elif daily_return >= self.daily_target * 0.6:  # 60% of target
            daily_mult = 0.7
        else:
            daily_mult = 1.0
        
        # Peak distance protection
        peak_distance = (self.peak_capital - self.capital) / self.peak_capital if self.peak_capital > 0 else 0
        peak_mult = max(0.4, 1 - (peak_distance * 2))
        
        # Winning streak scaling (gradually increase size with success)
        recent_trades = self.trade_history[-10:] if len(self.trade_history) >= 10 else self.trade_history
        if recent_trades:
            recent_wins = len([t for t in recent_trades if t['type'] == 'WIN'])
            recent_win_rate = recent_wins / len(recent_trades)
            
            if recent_win_rate >= 0.8:  # 80%+ win rate
                streak_mult = 1.1
            elif recent_win_rate >= 0.7:  # 70%+ win rate
                streak_mult = 1.05
            else:
                streak_mult = 0.9  # Reduce if win rate drops
        else:
            streak_mult = 1.0
        
        # Size reduction for approaching ultra-tight drawdown limit
        if current_dd > self.size_reduction_dd:
            size_reduction_factor = 0.4  # Cut size by 60%
        else:
            size_reduction_factor = 1.0
        
        # Apply all conservative multipliers with size reduction
        final_size = (base_size * confidence_mult * dd_protection * 
                     daily_mult * peak_mult * streak_mult * size_reduction_factor)
        
        # Ultra-conservative bounds
        final_size = min(final_size, self.capital * 0.02)   # Max 2% per trade (reduced from risk_cap)
        final_size = max(final_size, self.capital * 0.003)  # Minimum 0.3% per trade
        
        return final_size
    
    def trade(self, metrics):
        """Execute ultra-conservative trade"""
        if self.daily_trades >= self.max_daily_trades:
            return "⏸️ Conservative daily limit reached"
        
        # Daily target check
        daily_return = self.daily_profit / self.capital if self.capital > 0 else 0
        if daily_return >= self.daily_target:
            return f"✅ Conservative target achieved: {daily_return:.2%}"
        
        # Drawdown protection with ultra-tight limits
        current_dd = (self.initial_capital - self.capital) / self.initial_capital
        if current_dd > self.max_drawdown:
            return f"🛡️ Conservative drawdown limit: {current_dd:.2%} (Max: {self.max_drawdown:.1%})"
        
        # Market safety check
        if not self.can_trade(metrics):
            self.safety_violations += 1
            return "🟡 No trade — Conservative safety filters active"
        
        # Position sizing
        position_size = self.calculate_position_size(metrics)
        
        # Ultra-conservative execution
        confidence = metrics.get('ai_confidence', 0.5)
        trend_strength = metrics.get('trend_strength', 0.5)
        support_resistance = metrics.get('support_resistance', 0.5)
        regime = metrics.get('regime', 'unknown')
        
        # Conservative success probability (high baseline)
        base_success_prob = 0.65 + (confidence * 0.2)  # 65-85% range
        
        # Additional conservative bonuses
        trend_bonus = (trend_strength - 0.5) * 0.1  # Small trend bonus
        sr_bonus = (support_resistance - 0.5) * 0.1  # Small S/R bonus
        
        # Regime adjustments (conservative preferences)
        regime_adj = {
            'trending_bull': 1.1,
            'low_volatility': 1.15,  # Love low volatility
            'sideways': 1.0,
            'trending_bear': 0.95,
            'high_volatility': 0.0   # Never trade (filtered out earlier)
        }.get(regime, 0.9)
        
        final_success_prob = (base_success_prob + trend_bonus + sr_bonus) * regime_adj
        final_success_prob = min(0.88, max(0.60, final_success_prob))  # Conservative bounds
        
        # Execute trade
        if random.random() < final_success_prob:
            # WINNING TRADE - Conservative profit
            base_profit_pct = random.uniform(0.008, 0.020)  # Small, consistent profits
            
            # Conservative bonuses (smaller than other strategies)
            confidence_bonus = 1 + ((confidence - 0.75) * 0.2)  # Small confidence bonus
            
            # Regime profit adjustment
            regime_profit_adj = {
                'trending_bull': 1.15,
                'low_volatility': 1.1,
                'sideways': 1.0,
                'trending_bear': 1.05
            }.get(regime, 1.0)
            
            final_profit_pct = base_profit_pct * confidence_bonus * regime_profit_adj
            final_profit_pct = min(0.02, final_profit_pct)  # Reduced cap to 2%
            
            profit = position_size * final_profit_pct
            self.capital += profit
            self.daily_profit += profit
            
            # Update peak
            if self.capital > self.peak_capital:
                self.peak_capital = self.capital
            
            self.daily_trades += 1
            
            # Log trade
            trade_record = {
                'timestamp': datetime.utcnow().isoformat(),
                'type': 'WIN',
                'size': position_size,
                'profit': profit,
                'profit_pct': final_profit_pct,
                'confidence': confidence,
                'regime': regime
            }
            self.trade_history.append(trade_record)
            
            return f"💼 Conservative WIN | +${profit:.2f} ({final_profit_pct:.2%}) | Capital: ${self.capital:.2f} | Daily: {(self.daily_profit/self.capital):.2%} | Target: {self.daily_target:.1%}"
            
        else:
            # LOSING TRADE - Minimal loss
            base_loss_pct = self.stop_loss
            
            # Regime loss adjustment (very tight)
            regime_loss_adj = {
                'trending_bull': 0.8,
                'low_volatility': 0.7,  # Tightest stops in low vol
                'sideways': 1.0,
                'trending_bear': 0.9
            }.get(regime, 1.0)
            
            adjusted_loss_pct = base_loss_pct * regime_loss_adj
            adjusted_loss_pct = min(0.008, adjusted_loss_pct)  # Reduced cap to 0.8%
            
            loss = position_size * adjusted_loss_pct
            self.capital -= loss
            self.daily_profit -= loss
            self.daily_trades += 1
            
            # Log trade
            trade_record = {
                'timestamp': datetime.utcnow().isoformat(),
                'type': 'LOSS',
                'size': position_size,
                'loss': loss,
                'loss_pct': adjusted_loss_pct,
                'confidence': confidence,
                'regime': regime
            }
            self.trade_history.append(trade_record)
            
            return f"🔻 Conservative LOSS | -${loss:.2f} ({adjusted_loss_pct:.2%}) | Capital: ${self.capital:.2f} | Daily: {(self.daily_profit/self.capital):.2%}"
    
    def end_of_day_summary(self):
        """End of day processing for conservative strategy"""
        daily_return = self.daily_profit / self.capital if self.capital > 0 else 0
        
        # Track profitable days
        if self.daily_profit > 0:
            self.consecutive_profitable_days += 1
            self.total_profitable_days += 1
        else:
            self.consecutive_profitable_days = 0
        
        # Save daily history
        daily_summary = {
            'date': datetime.utcnow().strftime('%Y-%m-%d'),
            'return': daily_return,
            'profit': self.daily_profit,
            'trades': self.daily_trades,
            'target_achieved': daily_return >= self.daily_target,
            'safety_violations': self.safety_violations
        }
        
        self.daily_history.append(daily_summary)
        
        # Reset daily counters
        self.daily_profit = 0
        self.daily_trades = 0
        self.safety_violations = 0
        
        return daily_summary
    
    def get_status(self):
        """Comprehensive conservative strategy status"""
        current_dd = (self.initial_capital - self.capital) / self.initial_capital if self.initial_capital > 0 else 0
        total_return = (self.capital - self.initial_capital) / self.initial_capital if self.initial_capital > 0 else 0
        daily_return = self.daily_profit / self.capital if self.capital > 0 else 0
        
        # Calculate win rate
        wins = len([t for t in self.trade_history if t['type'] == 'WIN'])
        win_rate = wins / len(self.trade_history) if self.trade_history else 0
        
        # Calculate average daily return
        avg_daily_return = sum(d['return'] for d in self.daily_history) / len(self.daily_history) if self.daily_history else 0
        
        # Target achievement rate
        target_days = len([d for d in self.daily_history if d['target_achieved']])
        target_achievement_rate = target_days / len(self.daily_history) if self.daily_history else 0
        
        # Safety metrics
        total_trading_days = len(self.daily_history) if self.daily_history else 1
        safety_score = 1 - (self.safety_violations / max(1, self.daily_trades + self.safety_violations))
        
        return {
            "strategy": "ConservativeBot",
            "capital": self.capital,
            "initial_capital": self.initial_capital,
            "total_return": f"{total_return:.2%}",
            "daily_return": f"{daily_return:.2%}",
            "daily_target": f"{self.daily_target:.1%}",
            "target_progress": f"{(daily_return/self.daily_target)*100:.0f}%" if self.daily_target > 0 else "0%",
            "drawdown": f"{current_dd:.2%}",
            "max_drawdown_limit": f"{self.max_drawdown:.1%}",
            "trades_today": self.daily_trades,
            "total_trades": len(self.trade_history),
            "win_rate": f"{win_rate:.1%}",
            "target_win_rate": f"{self.min_win_rate_required:.1%}",
            "avg_daily_return": f"{avg_daily_return:.2%}",
            "consecutive_profitable_days": self.consecutive_profitable_days,
            "total_profitable_days": self.total_profitable_days,
            "target_achievement_rate": f"{target_achievement_rate:.1%}",
            "safety_score": f"{safety_score:.1%}",
            "peak_capital": self.peak_capital,
            "risk_level": "ULTRA_CONSERVATIVE",
            "ai_enhanced": True,
            "preserve_capital_mode": self.preserve_capital,
            "timestamp": datetime.utcnow().isoformat()
        }
