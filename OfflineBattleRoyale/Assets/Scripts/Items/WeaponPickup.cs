using UnityEngine;

public class WeaponPickup : LootItem
{
  [SerializeField] private WeaponId weaponId;

  protected override bool TryCollect(GameObject collector)
  {
    PlayerInventory inventory = collector.GetComponent<PlayerInventory>();
    if (inventory != null)
    {
      return inventory.TryPickupWeapon(weaponId);
    }

    BotInventory botInventory = collector.GetComponent<BotInventory>();
    if (botInventory != null)
    {
      return botInventory.TryPickupWeapon(weaponId);
    }

    return false;
  }
}
