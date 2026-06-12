using UnityEngine;

public class PlaneController : MonoBehaviour
{
  [SerializeField] private float flightSpeed = 40f;
  [SerializeField] private Vector3 flightStart = new Vector3(-400f, 150f, 0f);
  [SerializeField] private Vector3 flightEnd = new Vector3(400f, 150f, 0f);
  [SerializeField] private Transform planeModel;

  private Transform rider;
  private bool isFlying;
  private float flightProgress;

  public bool IsFlying => isFlying;

  public void BeginFlight(Transform playerTransform)
  {
    rider = playerTransform;
    isFlying = true;
    flightProgress = 0f;

    if (planeModel != null)
    {
      planeModel.position = flightStart;
    }

    if (rider != null)
    {
      rider.SetParent(planeModel != null ? planeModel : transform);
      rider.localPosition = Vector3.zero;
    }
  }

  private void Update()
  {
    if (!isFlying)
    {
      return;
    }

    flightProgress += (flightSpeed / Vector3.Distance(flightStart, flightEnd)) * Time.deltaTime;
    flightProgress = Mathf.Clamp01(flightProgress);

    Vector3 position = Vector3.Lerp(flightStart, flightEnd, flightProgress);
    if (planeModel != null)
    {
      planeModel.position = position;
      planeModel.LookAt(flightEnd);
    }

    bool jumpPressed = Input.GetKeyDown(KeyCode.Space) || Input.GetButtonDown("Jump");
    if (jumpPressed && rider != null)
    {
      DropRider();
    }

    if (flightProgress >= 1f)
    {
      DropRider();
    }
  }

  private void DropRider()
  {
    if (!isFlying || rider == null)
    {
      return;
    }

    isFlying = false;
    rider.SetParent(null);

    ParachuteController parachute = rider.GetComponent<ParachuteController>();
    if (parachute != null)
    {
      parachute.BeginDrop(0f);
    }

    GameManager.Instance?.OnPlayerJumpedFromPlane();
  }
}
