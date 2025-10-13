#!/usr/bin/env python3
"""
Тестовый скрипт для демонстрации работы системы цепей Маркова
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.markov_chain import CryptoMarkovChain
from modules.data_fetcher import CryptoDataFetcher
import pandas as pd
import numpy as np

def test_markov_system():
    """Тестирование системы цепей Маркова"""
    print("🧠 Тестирование системы цепей Маркова для криптовалют")
    print("=" * 60)
    
    # Создаем экземпляры
    data_fetcher = CryptoDataFetcher()
    markov_chain = CryptoMarkovChain()
    
    print("1. 📊 Загрузка данных...")
    
    # Загружаем демо-данные
    data = data_fetcher.fetch_data('BTC-USD', '1y')
    
    if data is not None:
        print(f"   ✅ Загружено {len(data)} записей")
        print(f"   📈 Цена: ${data['Close'].iloc[0]:.2f} → ${data['Close'].iloc[-1]:.2f}")
        
        print("\n2. 🔍 Определение состояний...")
        
        # Определяем состояния
        states = markov_chain.define_states(data)
        unique_states = list(set(states.values()))
        
        print(f"   ✅ Найдено {len(unique_states)} уникальных состояний")
        print(f"   📋 Примеры состояний:")
        for i, state in enumerate(unique_states[:5]):
            description = markov_chain.get_state_description(state)
            print(f"      {i+1}. {state}: {description}")
        
        print("\n3. 🔄 Построение матрицы переходов...")
        
        # Строим матрицу переходов
        transition_matrix = markov_chain.build_transition_matrix(data)
        
        print(f"   ✅ Матрица переходов построена ({transition_matrix.shape[0]}x{transition_matrix.shape[1]})")
        
        # Показываем статистику переходов
        non_zero_transitions = np.count_nonzero(transition_matrix)
        total_transitions = transition_matrix.size
        print(f"   📊 Ненулевых переходов: {non_zero_transitions}/{total_transitions} ({non_zero_transitions/total_transitions:.1%})")
        
        print("\n4. 🔮 Тестирование прогнозирования...")
        
        # Тестируем прогнозирование
        if unique_states:
            test_state = unique_states[0]
            print(f"   🎯 Тестируем прогноз из состояния: {test_state}")
            print(f"   📝 Описание: {markov_chain.get_state_description(test_state)}")
            
            try:
                predictions = markov_chain.predict_next_states(test_state, 5)
                
                print(f"   ✅ Прогноз успешно сгенерирован:")
                for pred in predictions:
                    print(f"      Шаг {pred['step']}: {pred['state']} (вероятность: {pred['probability']:.1%})")
                
            except Exception as e:
                print(f"   ❌ Ошибка при прогнозировании: {e}")
        
        print("\n5. 📊 Анализ частоты состояний...")
        
        # Анализируем частоту состояний
        freq_data = markov_chain.analyze_state_frequency()
        if not freq_data.empty:
            print(f"   ✅ Анализ завершен:")
            print(f"   🏆 Наиболее частое состояние: {freq_data.iloc[0]['Состояние']} ({freq_data.iloc[0]['Частота (%)']:.1f}%)")
            print(f"   📉 Наименее частое состояние: {freq_data.iloc[-1]['Состояние']} ({freq_data.iloc[-1]['Частота (%)']:.1f}%)")
        
        print("\n6. 💡 Торговые сигналы...")
        
        # Генерируем торговые сигналы
        if unique_states:
            test_state = unique_states[0]
            predictions = markov_chain.predict_next_states(test_state, 3)
            
            # Простой анализ сигналов
            signals = []
            for pred in predictions:
                state = pred['state']
                parts = state.split('_')
                if len(parts) >= 4:
                    trend = parts[0]
                    rsi = parts[2]
                    
                    if trend == 'T2' and rsi == 'R0':  # Рост + перепроданность
                        signals.append("🟢 ПОКУПКА")
                    elif trend == 'T0' and rsi == 'R2':  # Падение + перекупленность
                        signals.append("🔴 ПРОДАЖА")
                    else:
                        signals.append("⚪ НЕЙТРАЛЬНО")
            
            print(f"   📈 Торговые сигналы для состояния {test_state}:")
            for i, signal in enumerate(signals):
                print(f"      Шаг {i+1}: {signal}")
        
        print("\n" + "=" * 60)
        print("✅ Тестирование завершено успешно!")
        print("\n💡 Для полного функционала запустите:")
        print("   streamlit run app.py")
        print("   И перейдите в раздел '🧠 Цепи Маркова'")
        
    else:
        print("❌ Не удалось загрузить данные")

if __name__ == "__main__":
    test_markov_system()
