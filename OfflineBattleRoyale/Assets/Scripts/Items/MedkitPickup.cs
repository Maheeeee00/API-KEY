using UnityEngine;

public class MedkitPickup : LootItem
{
  protected override bool TryCollect(GameObject collector)
  {
    PlayerInventory inventory = collector.GetComponent<PlayerInventory>();
    if (inventory != null)
    {
      inventory.AddMedkit();
      return true;
    }

    BotInventory botInventory = collector.GetComponent<BotInventory>();
    if (botInventory != null)
    {
      botInventory.AddMedkit();
      return true;
    }

    return false;
  }
}
