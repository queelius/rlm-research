import asyncio
import time
import unittest

class DispatchTests(unittest.IsolatedAsyncioTestCase):
    async def test_pairs_are_sequential_complete_and_cancellation_settles(self):
        from collect import dispatch
        plan=[{'id':str(i),'pair_id':str(i//2),'pair_order':i%2} for i in range(16)]
        order=[];active=set();peak=0
        async def one(row):
            nonlocal peak
            self.assertNotIn(row['pair_id'],active);active.add(row['pair_id']);peak=max(peak,len(active))
            await asyncio.sleep(.001);order.append(row['id']);active.remove(row['pair_id'])
        await dispatch(plan,one,time.time()+2)
        self.assertEqual(set(order),{str(i) for i in range(16)});self.assertLessEqual(peak,4)
        for i in range(0,16,2):self.assertLess(order.index(str(i)),order.index(str(i+1)))
        settled=[]
        async def slow(row):
            try:await asyncio.sleep(10)
            finally:settled.append(row['id'])
        await dispatch(plan,slow,time.time()+.02)
        self.assertEqual(len(settled),4)

if __name__=='__main__':unittest.main()
