from nltk.translate.bleu_score import sentence_bleu
from nltk.translate.bleu_score import corpus_bleu
# reference = [['গাছের','গোঁড়ায়', 'একজন', 'পুরুষ', 'বসে', 'আছে'],['শার্ট', 'লুঙ্গি','পরা', 'একজন','লোক', 'একটা','বড়', 'বট','গাছের','নিচে', 'বসে', 'আছে']]
# candidate = ['একটা','ছোট','ছেলে','একটা','কাঠের','ভেতর','বসে', 'আছে']
# score = sentence_bleu(reference,candidate)
# print(score)


# reference = [[['গাছের','গোঁড়ায়', 'একজন', 'পুরুষ', 'বসে', 'আছে'],['শার্ট', 'লুঙ্গি','পরা', 'একজন','লোক', 'একটা','বড়', 'বট','গাছের','নিচে', 'বসে', 'আছে']]]
# candidate = [['একটা','ছোট','ছেলে','একটা','কাঠের','ভেতর','বসে', 'আছে']]
# score = corpus_bleu(reference,candidate)
# print(score)


reference = [['হলুদ', 'সরিষা','ক্ষেতের', 'মাঝে', 'দিয়ে', 'হেটে', 'যাচ্ছে', 'একজন', 'মহিলা']]
candidate = ['সরিষা', 'ক্ষেতের', 'মাঝে', 'একজন', 'মহিলা', 'দাঁড়িয়ে', 'আছে']
print('Individual 1-gram: %f' % sentence_bleu(reference, candidate, weights=(1, 0, 0, 0)))
print('Individual 2-gram: %f' % sentence_bleu(reference, candidate, weights=(0, 1, 0, 0)))
print('Individual 3-gram: %f' % sentence_bleu(reference, candidate, weights=(0, 0, 1, 0)))
print('Individual 4-gram: %f' % sentence_bleu(reference, candidate, weights=(0, 0, 0, 1)))


