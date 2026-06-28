        # Phase 3: Award to best bidder (highest confidence, lowest time)
        def score_bid(agent_bid):
            _, bid = agent_bid
            return bid["confidence"] - 0.1 * bid["estimatedSeconds"]

        winner_agent, winning_bid = max(valid_bids, key=score_bid)

