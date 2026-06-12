using UnityEngine;

public class GearPickup : LootItem
{
  [SerializeField] private GearType gearType;
  [SerializeField] private GearLevel gearLevel;

  protected override bool TryCollect(GameObject collector)
  {
    PlayerHealth playerHealth = collector.GetComponent<PlayerHealth>();
    PlayerInventory playerInventory = collector.GetComponent<PlayerInventory>();

    if (playerHealth != null && playerInventory != null)
    {
      ApplyGear(playerHealth, playerInventory);
      return true;
    }

    BotInventory botInventory = collector.GetComponent<BotInventory>();
    if (botInventory != null)
    {
      botInventory.ApplyGear(gearType, gearLevel);
      return true;
    }

    return false;
  }

  private void ApplyGear(PlayerHealth health, PlayerInventory inventory)
  {
    switch (gearType)
    {
      case GearType.Helmet:
        health.SetHelmet(gearLevel);
        break;
      case GearType.Vest:
        health.SetVest(gearLevel);
        break;
      case GearType.Backpack:
        inventory.SetBackpack(gearLevel);
        break;
    }
  }
}
