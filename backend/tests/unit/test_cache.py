from app.common.cache.states import UserProfile


def test_user_profile_create_different_instances():
    assert 1 == 1
    user_1 = UserProfile()
    user_1.created_cards.add(1)
    user_1.known_cards.add(2)
    user_1.master_cards.add(3)
    user_1.review_cards.append(4)
    user_2 = UserProfile()
    user_2.created_cards.add(5)
    user_2.known_cards.add(6)
    user_2.master_cards.add(7)
    user_2.review_cards.append(8)

    assert user_1 is not user_2

    assert user_1.created_cards != user_2.created_cards
    assert user_1.known_cards != user_2.known_cards
    assert user_1.master_cards != user_2.master_cards
    assert user_1.review_cards != user_2.review_cards
