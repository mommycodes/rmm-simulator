#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.markov_chain import CryptoMarkovChain
from modules.data_fetcher import CryptoDataFetcher
import pandas as pd
import numpy as np

def test_markov_system():
    print("🧠 Тестирование системы цепей Маркова для криптовалют")
    print("=" * 60)
    
    data_fetcher = CryptoDataFetcher()
    markov_chain = CryptoMarkovChain()
    
    print("1. 📊 Загрузка данных...")
    
    data = data_fetcher.fetch_data('BTC-USD', '1y')
    
    if data is not None:
        print(f"   ✅ Загружено {len(data)} записей")
        print(f"   📈 Цена: ${data['Close'].iloc[0]:.2f} → ${data['Close'].iloc[-1]:.2f}")
        
        print("\n2. 🔄 Обучение цепи Маркова...")
        
        markov_chain.train(data)
        
        print("   ✅ Обучение завершено")
        print(f"   📊 Состояний: {len(markov_chain.states)}")
        print(f"   🔗 Переходов: {len(markov_chain.transitions)}")
        
        print("\n3. 🔮 Генерация прогнозов...")
        
        predictions = markov_chain.predict(10)
        
        print("   ✅ Прогнозы сгенерированы")
        print("   📈 Следующие 10 дней:")
        
        for i, pred in enumerate(predictions, 1):
            print(f"      День {i}: {pred}")
        
        print("\n4. 📊 Анализ точности...")
        
        accuracy = markov_chain.evaluate_accuracy(data)
        
        print(f"   ✅ Точность: {accuracy:.2%}")
        
        print("\n5. 🎯 Рекомендации...")
        
        recommendations = markov_chain.get_recommendations()
        
        print("   ✅ Рекомендации получены")
        print("   💡 Рекомендации:")
        
        for rec in recommendations:
            print(f"      • {rec}")
        
        print("\n6. 📈 Визуализация...")
        
        try:
            markov_chain.plot_transitions()
            print("   ✅ График переходов сохранен")
        except Exception as e:
            print(f"   ⚠️ Ошибка визуализации: {e}")
        
        print("\n7. 💾 Сохранение модели...")
        
        try:
            markov_chain.save_model('markov_model.pkl')
            print("   ✅ Модель сохранена")
        except Exception as e:
            print(f"   ⚠️ Ошибка сохранения: {e}")
        
        print("\n8. 🔄 Загрузка модели...")
        
        try:
            new_markov = CryptoMarkovChain()
            new_markov.load_model('markov_model.pkl')
            print("   ✅ Модель загружена")
            
            new_predictions = new_markov.predict(5)
            print("   📈 Новые прогнозы:")
            for i, pred in enumerate(new_predictions, 1):
                print(f"      День {i}: {pred}")
                
        except Exception as e:
            print(f"   ⚠️ Ошибка загрузки: {e}")
        
        print("\n" + "=" * 60)
        print("🎉 Тестирование завершено успешно!")
        
    else:
        print("   ❌ Не удалось загрузить данные")
        print("   💡 Проверьте подключение к интернету")

def test_advanced_features():
    print("\n🔬 Тестирование расширенных функций")
    print("=" * 60)
    
    data_fetcher = CryptoDataFetcher()
    markov_chain = CryptoMarkovChain()
    
    print("1. 📊 Загрузка данных для разных символов...")
    
    symbols = ['BTC-USD', 'ETH-USD', 'ADA-USD']
    
    for symbol in symbols:
        data = data_fetcher.fetch_data(symbol, '6mo')
        if data is not None:
            print(f"   ✅ {symbol}: {len(data)} записей")
            
            markov_chain.train(data)
            predictions = markov_chain.predict(5)
            
            print(f"   📈 {symbol} прогнозы:")
            for i, pred in enumerate(predictions, 1):
                print(f"      День {i}: {pred}")
        else:
            print(f"   ❌ {symbol}: не удалось загрузить")
    
    print("\n2. 🔄 Тестирование разных периодов...")
    
    periods = ['1mo', '3mo', '6mo', '1y']
    
    for period in periods:
        data = data_fetcher.fetch_data('BTC-USD', period)
        if data is not None:
            markov_chain.train(data)
            accuracy = markov_chain.evaluate_accuracy(data)
            print(f"   📊 {period}: точность {accuracy:.2%}")
        else:
            print(f"   ❌ {period}: не удалось загрузить")
    
    print("\n3. 🎯 Тестирование рекомендаций...")
    
    data = data_fetcher.fetch_data('BTC-USD', '1y')
    if data is not None:
        markov_chain.train(data)
        recommendations = markov_chain.get_recommendations()
        
        print("   💡 Рекомендации:")
        for rec in recommendations:
            print(f"      • {rec}")
    
    print("\n" + "=" * 60)
    print("🎉 Расширенное тестирование завершено!")

if __name__ == "__main__":
    try:
        test_markov_system()
        test_advanced_features()
    except KeyboardInterrupt:
        print("\n🛑 Тестирование прервано пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()