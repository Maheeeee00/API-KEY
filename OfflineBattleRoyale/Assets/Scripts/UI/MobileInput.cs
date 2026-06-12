using UnityEngine;
using UnityEngine.EventSystems;

public class MobileInput : MonoBehaviour
{
  [SerializeField] private VirtualJoystick moveJoystick;
  [SerializeField] private VirtualJoystick lookJoystick;
  [SerializeField] private UIButton fireButton;
  [SerializeField] private UIButton jumpButton;
  [SerializeField] private UIButton healButton;
  [SerializeField] private UIButton reloadButton;
  [SerializeField] private UIButton sprintButton;

  public Vector2 MoveInput => moveJoystick != null ? moveJoystick.Direction : Vector2.zero;
  public Vector2 LookInput => lookJoystick != null ? lookJoystick.Direction : Vector2.zero;
  public bool FireHeld => fireButton != null && fireButton.IsPressed;
  public bool JumpPressed => jumpButton != null && jumpButton.WasPressedThisFrame;
  public bool HealPressed => healButton != null && healButton.WasPressedThisFrame;
  public bool ReloadPressed => reloadButton != null && reloadButton.WasPressedThisFrame;
  public bool SprintHeld => sprintButton != null && sprintButton.IsPressed;
}

public class VirtualJoystick : MonoBehaviour, IDragHandler, IPointerUpHandler, IPointerDownHandler
{
  [SerializeField] private RectTransform handle;
  [SerializeField] private float handleRange = 60f;

  private RectTransform rectTransform;
  private Vector2 direction;

  public Vector2 Direction => direction;

  private void Awake()
  {
    rectTransform = GetComponent<RectTransform>();
  }

  public void OnPointerDown(PointerEventData eventData)
  {
    OnDrag(eventData);
  }

  public void OnDrag(PointerEventData eventData)
  {
    Vector2 localPoint;
    if (RectTransformUtility.ScreenPointToLocalPointInRectangle(rectTransform, eventData.position, eventData.pressEventCamera, out localPoint))
    {
      Vector2 clamped = Vector2.ClampMagnitude(localPoint, handleRange);
      if (handle != null)
      {
        handle.anchoredPosition = clamped;
      }

      direction = clamped / handleRange;
    }
  }

  public void OnPointerUp(PointerEventData eventData)
  {
    direction = Vector2.zero;
    if (handle != null)
    {
      handle.anchoredPosition = Vector2.zero;
    }
  }
}

public class UIButton : MonoBehaviour, IPointerDownHandler, IPointerUpHandler
{
  public bool IsPressed { get; private set; }
  public bool WasPressedThisFrame { get; private set; }

  private void LateUpdate()
  {
    WasPressedThisFrame = false;
  }

  public void OnPointerDown(PointerEventData eventData)
  {
    if (!IsPressed)
    {
      WasPressedThisFrame = true;
    }

    IsPressed = true;
  }

  public void OnPointerUp(PointerEventData eventData)
  {
    IsPressed = false;
  }
}
